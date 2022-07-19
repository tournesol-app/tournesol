import csv
import zipfile
from io import StringIO

from django.db.models import Count, F
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from drf_spectacular.utils import OpenApiTypes, extend_schema
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.views import APIView

from core.models import User
from tournesol.entities.base import UID_DELIMITER
from tournesol.lib.public_dataset import get_dataset
from tournesol.models import Comparison, Poll
from tournesol.serializers.comparison import ComparisonSerializer
from tournesol.utils.cache import cache_page_no_i18n
from tournesol.views.mixins.poll import PollScopedViewMixin


def write_comparisons_file(request, write_target):
    """
    Writes a user's comparisons as a CSV file to write_target which can be
    among other options an HttpResponse or a StringIO
    """
    fieldnames = ["video_a", "video_b", "criteria", "weight", "score"]
    writer = csv.DictWriter(write_target, fieldnames=fieldnames)
    writer.writeheader()
    comparisons = (
        Comparison.objects.filter(user=request.user)
        .select_related("entity_1", "entity_2")
        .prefetch_related("criteria_scores")
    )
    serialized_comparisons = ComparisonSerializer(comparisons, many=True).data

    writer.writerows(
        {
            "video_a": comparison["entity_a"]["uid"].split(UID_DELIMITER)[1],
            "video_b": comparison["entity_b"]["uid"].split(UID_DELIMITER)[1],
            **criteria_score,
        }
        for comparison in serialized_comparisons
        for criteria_score in comparison["criteria_scores"]
    )


def write_public_comparisons_file(poll_name: str, write_target) -> None:
    """
    Retrieve all public comparisons' data, and write them as CSV in
    `write_target`, an object supporting the Python file API.
    """
    fieldnames = [
        "public_username",
        "video_a",
        "video_b",
        "criteria",
        "weight",
        "score",
    ]
    writer = csv.DictWriter(write_target, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(
        {
            "public_username": comparison.username,
            "video_a": comparison.uid_a.split(UID_DELIMITER)[1],
            "video_b": comparison.uid_b.split(UID_DELIMITER)[1],
            "criteria": comparison.criteria,
            "weight": comparison.weight,
            "score": comparison.score,
        }
        for comparison in get_dataset(poll_name).iterator()
    )


class ExportComparisonsView(APIView):
    """Export all the comparisons made by the logged user in a CSV file."""
    permission_classes = [IsAuthenticated]
    throttle_scope = "api_users_me_export"

    @extend_schema(
        description="Download the current user's comparisons in a .csv file",
        responses={200: OpenApiTypes.BINARY},
    )
    def get(self, request):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="export.csv"'
        write_comparisons_file(request, response)
        return response


class ExportPublicComparisonsView(APIView):
    """Export all the public comparisons made by any user."""
    permission_classes = [AllowAny]
    throttle_scope = "api_export_comparisons"

    @method_decorator(cache_page_no_i18n(60 * 10))  # 10 minutes cache
    @extend_schema(
        description="Download public data in .csv file",
        responses={200: OpenApiTypes.BINARY},
    )
    def get(self, request):
        response = HttpResponse(content_type="text/csv")
        response[
            "Content-Disposition"
        ] = 'attachment; filename="tournesol_public_export.csv"'
        write_public_comparisons_file(Poll.default_poll().name, response)
        return response


class ExportAllView(APIView):
    """Export all the logged user's data in a .zip file."""
    throttle_scope = "api_users_me_export"

    @extend_schema(
        description="Download the current user's data in a .zip file",
        responses={200: OpenApiTypes.BINARY},
    )
    def get(self, request):
        # Folder name in ZIP archive which contains the above files
        zip_root = f"export_{request.user.username}"

        response = HttpResponse(content_type="application/x-zip-compressed")
        response["Content-Disposition"] = f"attachment; filename={zip_root}.zip"

        with zipfile.ZipFile(response, "w", compression=zipfile.ZIP_DEFLATED) as zip_file:
            # Currently, adds only a single file to the zip archive, but we may extend the
            # content of the export in the future
            with StringIO() as comparisons_file_like:
                write_comparisons_file(request, comparisons_file_like)
                zip_file.writestr(f"{zip_root}/comparisons.csv", comparisons_file_like.getvalue())

        return response


class ExportProofOfVoteView(PollScopedViewMixin, APIView):
    """Export to the admin all the proofs of vote for a given poll."""
    authentication_classes = [SessionAuthentication]  # Auth via Django Admin session
    permission_classes = [IsAdminUser]

    @extend_schema(
        description="Download .csv file with proof of vote signatures",
        responses={200: OpenApiTypes.BINARY},
    )
    def get(self, request, *args, **kwargs):
        poll = self.poll_from_url
        response = HttpResponse(content_type="text/csv")
        response[
            "Content-Disposition"
        ] = f'attachment; filename="proof_of_vote_{poll.name}.csv"'

        fieldnames = [
            "user_id",
            "username",
            "email",
            "n_comparisons",
            "signature",
        ]
        writer = csv.DictWriter(response, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(
            {**d, "signature": poll.get_proof_of_vote(d["user_id"])}
            for d in User.objects.filter(comparisons__poll=poll).values(
                "username", "email", n_comparisons=Count("*"), user_id=F("id")
            )
        )
        return response
