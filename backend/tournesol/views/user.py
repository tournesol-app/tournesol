import csv
import logging

from django.contrib.auth import logout
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema

from tournesol.serializers import ComparisonSerializer
from tournesol.models import Comparison


logger = logging.getLogger(__name__)


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={204: None})
    def delete(self, request):
        """
        Delete and logout the authenticated user.
        All related resources are also deleted: comparisons, rate-later list, access tokens, etc.
        """
        user = request.user
        user.delete()
        logout(request)
        logger.info("User '%s' with email '%s' has been deleted.", user.username, user.email)
        return Response(status=status.HTTP_204_NO_CONTENT)




class UserDataDumpView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="export.csv"'
        writer = csv.DictWriter(response, fieldnames=['video_a', 'video_b', 'criteria', 'weight', 'score'])
        writer.writeheader()
                
        comparison_queryset = Comparison.objects.filter(user=request.user)
        serialized_comparisons = [ComparisonSerializer(comparison).data for comparison in comparison_queryset]

        writer.writerows(
            { 
                "video_a": comparison["video_a"]["video_id"],
                "video_b": comparison["video_b"]["video_id"],
                **criteria_score
            }
            for comparison in serialized_comparisons
            for criteria_score in comparison['criteria_scores']
        )
        return response
