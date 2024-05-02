import csv
import zipfile
from io import StringIO
from os.path import getctime
from pathlib import Path

from django.conf import settings
from django.db.models import Count, F
from django.http import HttpResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from drf_spectacular.utils import OpenApiTypes, extend_schema
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.views import APIView

from core.models import User
from core.utils.time import time_ago
from tournesol.entities.base import UID_DELIMITER
from tournesol.lib.public_dataset import write_comparisons_file
from tournesol.models import Comparison, Poll
from tournesol.models.poll import PROOF_OF_VOTE_KEYWORD
from tournesol.serializers.comparison import ComparisonSerializer
from tournesol.utils.cache import cache_page_no_i18n
from tournesol.views.mixins.poll import PollScopedViewMixin


def write_logged_user_comparisons_file(request, write_target):
    """
    Write all user's comparisons as a CSV file to `write_target` which can be
    among other options an HttpResponse or a StringIO.

    Comparisons from all polls are included.
    """
    fieldnames = ["video_a", "video_b", "criteria", "weight", "score", "score_max"]
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


class ExportComparisonsView(APIView):
    """
    Export all comparisons made in all polls by the logged user as a CSV file.
    """

    permission_classes = [IsAuthenticated]
    throttle_scope = "api_users_me_export"

    @extend_schema(
        description="Download all comparisons made in all polls by the logged-in user in a"
        " CSV file.",
        responses={200: OpenApiTypes.BINARY},
    )
    def get(self, request):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="export.csv"'
        write_logged_user_comparisons_file(request, response)
        return response


class ExportPublicComparisonsView(APIView):
    """
    Export all public comparisons made in the default poll by all users as a CSV file.
    """

    permission_classes = [AllowAny]
    throttle_scope = "api_export_comparisons"

    @method_decorator(cache_page_no_i18n(60 * 10))  # 10 minutes cache
    @extend_schema(
        description="Download all public comparisons made in the `videos` poll by all users in a"
        " CSV file.",
        responses={200: OpenApiTypes.BINARY},
    )
    def get(self, request):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="tournesol_public_export.csv"'
        first_day_of_week = time_ago(days=timezone.now().weekday()).date()
        write_comparisons_file(Poll.default_poll().name, response, first_day_of_week)
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

        response = HttpResponse(content_type="application/zip")
        response["Content-Disposition"] = f"attachment; filename={zip_root}.zip"

        with zipfile.ZipFile(response, "w", compression=zipfile.ZIP_DEFLATED) as zip_file:
            # Currently, adds only a single file to the zip archive, but we may extend the
            # content of the export in the future
            with StringIO() as comparisons_file_like:
                write_logged_user_comparisons_file(request, comparisons_file_like)
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
        response["Content-Disposition"] = f'attachment; filename="proof_of_vote_{poll.name}.csv"'

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
            {**d, "signature": poll.get_user_proof(d["user_id"], PROOF_OF_VOTE_KEYWORD)}
            for d in User.objects.filter(comparisons__poll=poll).values(
                "username", "email", n_comparisons=Count("*"), user_id=F("id")
            )
        )
        return response


class ExportPublicAllView(APIView):
    """
    Export the complete public dataset in a .zip file.
    """

    throttle_scope = "api_export_comparisons"
    permission_classes = [AllowAny]

    @extend_schema(
        description="Download the complete public dataset of the `videos` poll in a .zip file.",
        responses={200: OpenApiTypes.BINARY},
    )
    def get(self, request):
        dataset_base_name = settings.APP_TOURNESOL["DATASET_BASE_NAME"]
        datasets_build_dir = Path(settings.MEDIA_ROOT).joinpath(
            settings.APP_TOURNESOL["DATASETS_BUILD_DIR"]
        )

        all_datasets = datasets_build_dir.glob(f"{dataset_base_name}*.zip")

        try:
            latest_dataset = max(all_datasets, key=getctime)
        except ValueError as error:
            raise NotFound("No dataset available.") from error

        with open(latest_dataset, "rb") as archive:
            archive_content = archive.read()

        response = HttpResponse(content_type="application/zip")
        response[
            "Content-Disposition"
        ] = f"attachment; filename={latest_dataset.name}"
        response.content = archive_content
        return response
