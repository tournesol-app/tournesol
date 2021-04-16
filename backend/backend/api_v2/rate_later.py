from backend.api_v2.helpers import WithUpdatedDocstringsDecorator, WithPKOverflowProtection
from backend.models import Video, UserPreferences
from backend.models import VideoRateLater
from django_filters import rest_framework as filters
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, extend_schema_field, inline_serializer
from rest_framework import mixins
from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .helpers import video_get_or_create_verify_raise
from .videos import VideoSerializerV2


class VideoRateLaterSerializerV2(serializers.HyperlinkedModelSerializer):
    """Serialize rate later objects."""

    id = serializers.IntegerField(read_only=True,
                                  help_text="ID of the video rate later object")

    video = serializers.SlugRelatedField(
        slug_field="video_id",
        help_text="Youtube Video ID",
        read_only=False,
        queryset=Video.objects.all())

    username = serializers.SerializerMethodField(
        help_text="User username", read_only=True, required=False)

    datetime_add = serializers.DateTimeField(help_text="When video was added",
                                             read_only=True)

    video_info = VideoSerializerV2(read_only=True)

    @extend_schema_field(OpenApiTypes.STR)
    def get_username(self, obj):
        return obj.user.username

    def to_representation(self, obj):
        data = super(VideoRateLaterSerializerV2, self).to_representation(obj)
        data['video_info'] = VideoSerializerV2(obj.video).data
        return data

    def is_valid(self, *args, **kwargs):
        # creating the video object in case if it does not exist
        video_get_or_create_verify_raise(video_id=self.initial_data.get('video', ''),
                                         field='video')
        return super(VideoRateLaterSerializerV2, self).is_valid(*args, **kwargs)

    def create(self, validated_data):
        user = UserPreferences.objects.get(user__username=self.context['request'].user.username)
        video = validated_data['video']
        if isinstance(video, str):
            video = Video.objects.get(video_id=video)
        vrl = VideoRateLater.objects.create(user=user, video=video)
        return vrl

    class Meta:
        model = VideoRateLater
        fields = [
            'id',
            'video',
            'username',
            'datetime_add',
            'video_info']


class VideoRateLaterFilterV2(filters.FilterSet):
    """Filter rate later objects."""

    class Meta:
        model = VideoRateLater
        fields = ['video__video_id']


@WithUpdatedDocstringsDecorator
class VideoRateLaterViewSetV2(mixins.CreateModelMixin,
                              mixins.ListModelMixin,
                              mixins.RetrieveModelMixin,
                              mixins.DestroyModelMixin,
                              WithPKOverflowProtection,
                              viewsets.GenericViewSet, ):
    """Get/set rate the personal later list."""

    UPDATE_DOCSTRING = {
        'list': "Get videos queued to be rated later",
        'retrieve': "Get one video to be rated later (by object ID)",
        'create': "Schedule a video to be rated later",
        'destroy': "Remove a video from rate later list"}

    KWARGS_DICT = {
        'create': {
            'responses': {
                400: None, 201: VideoRateLaterSerializerV2}}, 'retrieve': {
            'responses': {
                404: None, 200: VideoRateLaterSerializerV2}}, 'list': {
            'responses': {
                200: VideoRateLaterSerializerV2(many=True),
                400: None, 404: None}}, 'destroy': {
            'responses': {
                204: None, 404: None, 400: None}}}

    serializer_class = VideoRateLaterSerializerV2
    permission_classes = [IsAuthenticated]
    filterset_class = VideoRateLaterFilterV2

    def get_queryset(self, pk=None):
        """Only my rate later objects."""
        qs = VideoRateLater.objects.all()

        qs = qs.filter(user__user__username=self.request.user.username)

        return qs

    @extend_schema(
        request=inline_serializer("VideoRateLaterDelete",
                                  fields={'video_id': serializers.CharField(
                                      help_text="Video id")},
                                  many=True),
        responses={200: None,
                   400: None})
    @action(methods=['PATCH'], detail=False, name="Bulk delete videos by IDs")
    def bulk_delete(self, request):
        """Delete many videos from the list by IDs."""
        video_ids = []

        if not isinstance(request.data, list):
            return Response({'detail': f"Request is not a list: {str(request.data)}"}, status=400)

        for entry in request.data:
            if isinstance(entry, str):
                video_ids.append(entry)
            elif isinstance(entry, dict):
                if 'video_id' in entry:
                    video_ids.append(entry['video_id'])
                else:
                    return Response({'detail': "Dictionary request, but no video_id field"},
                                    status=400)
            else:
                return Response({'detail': "Unknown request"}, status=400)

        deleted, _ = VideoRateLater.objects.filter(user__user__username=request.user.username,
                                                   video__video_id__in=video_ids).delete()

        return Response({'received': len(video_ids),
                         'deleted': deleted}, status=200)
