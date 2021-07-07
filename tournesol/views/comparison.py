from django.db.models import Q
from django.shortcuts import get_object_or_404

from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from ..models import Comparison, ComparisonCriteriaScore, Video
from ..serializers import ComparisonSerializer, ComparisonSerializerInverse


class ComparisonViewSet(viewsets.ModelViewSet):
    queryset = Comparison.objects.all()
    serializer_class = ComparisonSerializer

    def get_queryset(self):
        return Comparison.objects.filter(user=self.request.user)

    @action(methods=['get'], detail=False)
    def get_comparison(self, request, *args, **kwargs):
        """
        Get one comparison with both videos_id
        """
        video_1 = request.query_params.get('video_1', None)
        video_2 = request.query_params.get('video_2', None)
        comparisons = Comparison.objects.filter(video_1__video_id=video_1, video_2__video_id=video_2, user=request.user)
        if comparisons:
            return Response(ComparisonSerializer(comparisons.first()).data)
        # test with opposite
        comparisons = Comparison.objects.filter(video_1__video_id=video_2, video_2__video_id=video_1, user=request.user)
        if comparisons:
            return Response(ComparisonSerializerInverse(comparisons.first()).data)
        return Response('No comparison found', status=404)

    @action(methods=['get'], detail=False)
    def list_comparison(self, request, *args, **kwargs):
        """
        Get a liste of comparison with video_id as search parameter
        """
        video = request.query_params.get('video')
        limit = request.query_params.get('limit') if request.query_params.get('limit') and \
                                                     request.query_params.get('limit').isdigit() else 100
        offset = request.query_params.get('offset') if request.query_params.get('offset') and \
                                                     request.query_params.get('offset').isdigit() else 0
        comparisons = self.queryset[offset:limit] if not video \
            else self.queryset.filter(Q(video_1__video_id=video) | Q(video_2__video_id=video))[offset:limit]
        if not comparisons:
            return Response('No comparison found', status=404)
        return Response(ComparisonSerializer(comparisons, many=True).data)

    def create(self, request, *args, **kwargs):
        video_1_id = request.data.get("video_1", "")
        video_1 = get_object_or_404(Video, video_id=video_1_id)
        video_2_id = request.data.get("video_2", "")
        video_2 = get_object_or_404(Video, video_id=video_2_id)
        criterias = request.data.get("criteria_scores", [])
        duration_ms = request.data.get("duration_ms", 0)
        comparisons = Comparison.objects.filter(video_1__video_id=video_1_id, video_2__video_id=video_2_id, user=request.user)
        comparisons_inv = Comparison.objects.filter(video_1__video_id=video_2_id, video_2__video_id=video_1_id, user=request.user)
        if comparisons or comparisons_inv:
            return self.update(request, *args, **kwargs)
        comparison = Comparison(video_1=video_1, video_2=video_2, user=request.user, duration_ms=duration_ms)
        comparison.save()
        [ComparisonCriteriaScore(comparison=comparison, criteria=criteria['criteria'], score=criteria['score'],
                                    weight=criteria['weight']).save() for criteria in criterias]
        comparison.refresh_from_db()
        return Response(ComparisonSerializer(comparison).data)

    def update(self, request, *args, **kwargs):
        video_1_id = request.data.get("video_1", "")
        get_object_or_404(Video, video_id=video_1_id)
        video_2_id = request.data.get("video_2", "")
        get_object_or_404(Video, video_id=video_2_id)
        criterias = request.data.get("criteria_scores", [])
        duration_ms = request.data.get("duration_ms", 0)
        comparisons = Comparison.objects.filter(video_1__video_id=video_1_id, video_2__video_id=video_2_id,
                                                 user=request.user)
        comparisons_inv = Comparison.objects.filter(video_1__video_id=video_2_id, video_2__video_id=video_1_id,
                                                     user=request.user)
        if not comparisons and not comparisons_inv:
            return self.create(request, *args, **kwargs)
        if comparisons:
            comparison = comparisons.first()
            reverse = False
        else:
            comparison = comparisons_inv.first()
            reverse = True
        comparison.duration_ms = duration_ms
        comparison.save()
        ComparisonCriteriaScore.objects.filter(comparison=comparison).delete()
        for criteria in criterias:
            score = criteria['score'] if not reverse else criteria['score']*-1
            ComparisonCriteriaScore(comparison=comparison, criteria=criteria['criteria'], score=score,
                                    weight=criteria['weight']).save()
        comparison.refresh_from_db()
        return Response(ComparisonSerializer(comparison).data)
