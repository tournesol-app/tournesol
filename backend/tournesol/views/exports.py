import csv
import zipfile
from io import StringIO

from django.http import HttpResponse
from django.utils.decorators import method_decorator
from drf_spectacular.utils import OpenApiTypes, extend_schema
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from tournesol.models import Comparison, ContributorRating
from tournesol.serializers.comparison import ComparisonSerializer
from tournesol.utils.cache import cache_page_no_i18n


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
            "video_a": comparison["entity_a"]["video_id"],
            "video_b": comparison["entity_b"]["video_id"],
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
    public_data = ContributorRating.objects.filter(is_public=True).select_related(
        "user", "entity"
    )
    serialized_comparisons = []
    public_videos = set((rating.user, rating.entity) for rating in public_data)
    comparisons = (
        Comparison.objects.all()
        .select_related("entity_1", "entity_2", "user")
        .prefetch_related("criteria_scores")
    )
    public_comparisons = [
        comparison
        for comparison in comparisons
        if (
            (comparison.user, comparison.entity_1) in public_videos
            and (comparison.user, comparison.entity_2) in public_videos
        )
    ]
    public_usernames = [comparison.user.username for comparison in public_comparisons]
    serialized_comparisons = ComparisonSerializer(public_comparisons, many=True).data
    writer.writerows(
        {
            "public_username": public_username,
            "video_a": comparison["entity_a"]["video_id"],
            "video_b": comparison["entity_b"]["video_id"],
            **criteria_score,
        }
        for (public_username, comparison) in zip(
            public_usernames, serialized_comparisons
        )
        for criteria_score in comparison["criteria_scores"]
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
