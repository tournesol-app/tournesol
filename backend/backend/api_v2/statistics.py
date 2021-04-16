from backend.models import ExpertRating, Video, UserInformation
from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from backend.rating_fields import VIDEO_FIELDS
from django.db.models import Min, Max, F
from backend.api_v2.helpers import WithPKOverflowProtection


class StatisticsSerializerV2(serializers.Serializer):
    """Serialize statistics for the website."""
    certified_experts = serializers.IntegerField(
        help_text="Number of experts with certified e-mails")
    pairwise_comparisons = serializers.IntegerField(
        help_text="Total number of pairwise comparisons")
    videos = serializers.IntegerField(
        help_text="Total number of videos in the database")
    min_score = serializers.FloatField(
        help_text="Minimal aggregated score over all videos and features")
    max_score = serializers.FloatField(
        help_text="Maximal aggregated score over all videos and features")


class StatisticsViewSetV2(viewsets.ViewSet, WithPKOverflowProtection):
    """Show website statistics."""
    serializer_class = StatisticsSerializerV2
    permission_classes = [IsAuthenticatedOrReadOnly]

    # need a list, otherwise router will not register this viewset
    @extend_schema(exclude=True, responses={
                200: StatisticsSerializerV2(
                    many=True),
                400: None})
    def list(self, request):
        return Response({})

    @extend_schema(
        responses={
            200: StatisticsSerializerV2(
                many=False)},
        operation_id="view")
    @action(methods=['GET'], detail=False)
    def view(self, request):
        """Get statistics for the website."""
        minmax_scores = \
            Video.objects.aggregate(**{'max_' + f: Max(F(f)) for f in VIDEO_FIELDS},
                                    **{'min_' + f: Min(F(f)) for f in VIDEO_FIELDS})

        try:
            min_score = min([v for k, v in minmax_scores.items() if k.startswith('min')])
            max_score = max([v for k, v in minmax_scores.items() if k.startswith('max')])
        except Exception:
            min_score = 0.0
            max_score = 0.0

        data = {'certified_experts': UserInformation.
                _annotate_is_certified(UserInformation.objects.all())
                .filter(_is_certified=1, user__is_active=True).count(),
                'pairwise_comparisons': ExpertRating.objects.all().count(),
                'videos': Video.objects.all().count(),
                'min_score': min_score,
                'max_score': max_score}

        return Response(StatisticsSerializerV2(data, many=False).data)
