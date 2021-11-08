import csv
import zipfile
from io import StringIO

from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from tournesol.serializers import ComparisonSerializer
from tournesol.models import Comparison


def write_comparisons_file(request, write_target):
    """
    Writes a user's comparisons as a CSV file to write_target which can be
    among other options an HttpResponse or a StringIO
    """
    fieldnames = ['video_a', 'video_b', 'criteria', 'weight', 'score']
    writer = csv.DictWriter(write_target, fieldnames=fieldnames)
    writer.writeheader()
    comparisons = Comparison.objects.filter(user=request.user)\
        .select_related("video_1", "video_2")\
        .prefetch_related("criteria_scores")
    serialized_comparisons = [ComparisonSerializer(comparison).data for comparison in comparisons]

    writer.writerows(
        {
            "video_a": comparison["video_a"]["video_id"],
            "video_b": comparison["video_b"]["video_id"],
            **criteria_score
        }
        for comparison in serialized_comparisons
        for criteria_score in comparison['criteria_scores']
    )


class ExportComparisonsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="export.csv"'
        write_comparisons_file(request, response)
        return response


class ExportAllView(APIView):

    def get(self, request):
        # Folder name in ZIP archive which contains the above files
        zip_root = f"export_{request.user.username}"

        response = HttpResponse(content_type="application/x-zip-compressed")
        response['Content-Disposition'] = f'attachment; filename={zip_root}.zip'

        zf = zipfile.ZipFile(response, "w", compression=zipfile.ZIP_DEFLATED)

        # Currently adds only a single file to the zip archive, but we may extend the
        # content of the export in the future
        with StringIO() as comparisons_file_like:
            write_comparisons_file(request, comparisons_file_like)
            zf.writestr(f'{zip_root}/comparisons.csv', comparisons_file_like.getvalue())

        # Close zip for all contents to be written
        zf.close()

        return response
