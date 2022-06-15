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
from tournesol.models import Comparison, ContributorRating
from tournesol.models.poll import DEFAULT_POLL_NAME
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


def write_public_comparisons_file(request, write_target):
    """
    Writes all public comparisons data as a CSV file to write_target which can be
    among other options an HttpResponse or a StringIO
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

    comparisons = Comparison.objects.raw(
        """
        SELECT
            tournesol_comparison.id,

            core_user.username,
            entity_1.uid AS entity_a,
            entity_2.uid AS entity_b,
            comparisoncriteriascore.criteria,
            comparisoncriteriascore.weight,
            comparisoncriteriascore.score

        FROM tournesol_comparison

        -- this JOIN allows to filter on the desired poll
        JOIN tournesol_poll
          ON tournesol_poll.id = tournesol_comparison.poll_id

        JOIN core_user
          ON core_user.id = tournesol_comparison.user_id

        JOIN tournesol_comparisoncriteriascore AS comparisoncriteriascore
          ON comparisoncriteriascore.comparison_id = tournesol_comparison.id

        JOIN tournesol_entity AS entity_1
          ON entity_1.id = tournesol_comparison.entity_1_id

        JOIN tournesol_entity AS entity_2
          ON entity_2.id = tournesol_comparison.entity_2_id

        -- this JOIN allows to filter by public ratings for the entity_1
        -- the poll has been already filtered, no need to filter it again
        JOIN tournesol_contributorrating AS rating_1
          ON rating_1.entity_id = tournesol_comparison.entity_1_id
         AND rating_1.user_id = tournesol_comparison.user_id

        -- this JOIN allows to filter by public ratings for the entity_2
        -- the poll has been already filtered, no need to filter it again
        JOIN tournesol_contributorrating AS rating_2
          ON rating_2.entity_id = tournesol_comparison.entity_2_id
         AND rating_2.user_id = tournesol_comparison.user_id

        WHERE tournesol_poll.name = 'videos'
          -- keep only public ratings
          AND rating_1.is_public = true
          AND rating_2.is_public = true;
        """
    )
    writer.writerows(
        {
            "public_username": comparison.username,
            "video_a": comparison.uid_a.split(UID_DELIMITER)[1],
            "video_b": comparison.uid_b.split(UID_DELIMITER)[1],
            "criteria": comparison.criteria,
            "weight": comparison.weight,
            "score": comparison.score,
        }
        for comparison in comparisons
    )


class ExportComparisonsView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_scope = "api_users_me_export"

    @extend_schema(
        description="Download current user data in .zip file",
        responses={200: OpenApiTypes.BINARY},
    )
    def get(self, request):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="export.csv"'
        write_comparisons_file(request, response)
        return response


class ExportPublicComparisonsView(APIView):
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
        write_public_comparisons_file(request, response)
        return response


class ExportAllView(APIView):
    throttle_scope = "api_users_me_export"

    @extend_schema(
        description="Download current user data in .zip file",
        responses={200: OpenApiTypes.BINARY},
    )
    def get(self, request):
        # Folder name in ZIP archive which contains the above files
        zip_root = f"export_{request.user.username}"

        response = HttpResponse(content_type="application/x-zip-compressed")
        response["Content-Disposition"] = f"attachment; filename={zip_root}.zip"

        zf = zipfile.ZipFile(response, "w", compression=zipfile.ZIP_DEFLATED)

        # Currently adds only a single file to the zip archive, but we may extend the
        # content of the export in the future
        with StringIO() as comparisons_file_like:
            write_comparisons_file(request, comparisons_file_like)
            zf.writestr(f"{zip_root}/comparisons.csv", comparisons_file_like.getvalue())

        # Close zip for all contents to be written
        zf.close()

        return response


class ExportProofOfVoteView(PollScopedViewMixin, APIView):
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
