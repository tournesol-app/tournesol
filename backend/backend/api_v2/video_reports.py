import logging

from backend.api_v2.helpers import get_user_preferences, WithUpdatedDocstringsDecorator, \
    WithPKOverflowProtection
from backend.models import VideoReports, Video
from backend.rating_fields import VIDEO_REPORT_FIELDS
from django.db import transaction
from django.db.utils import IntegrityError
from django_filters import rest_framework as filters
from rest_framework import mixins
from rest_framework import serializers, viewsets


class VideoReportsSerializerV2(serializers.HyperlinkedModelSerializer):
    """Serialize VideoReports."""

    video = serializers.SlugRelatedField(
        slug_field="video_id",
        read_only=False,
        queryset=Video.objects.all())

    class Meta:
        model = VideoReports
        fields = ['id', 'video', 'explanation'] + \
            sorted(VIDEO_REPORT_FIELDS.keys())
        read_only_fields = ['id']


class VideoReportsFilterV2(filters.FilterSet):
    """Filter video reports."""

    only_mine = filters.BooleanFilter(method="my_reports",
                                      field_name='user__user__username',
                                      help_text="Only show reports by me.")

    def my_reports(self, queryset, name, value):
        """Only show my reports."""
        print(name, value)
        if value:
            queryset = queryset.filter(user__user__username=self.request.user.username)
        return queryset

    class Meta:
        model = VideoReports
        fields = ['video__video_id', 'only_mine']


@WithUpdatedDocstringsDecorator
class VideoReportsViewSetV2(mixins.RetrieveModelMixin,
                            mixins.ListModelMixin,
                            mixins.CreateModelMixin,
                            mixins.UpdateModelMixin,
                            WithPKOverflowProtection,
                            viewsets.GenericViewSet, ):
    """Report videos and show reports [DEPRECATED]."""

    UPDATE_DOCSTRING = {
        'list': "Show all anonymized video reports",
        'retrieve': "Get one video report",
        'create': "Report a video",
        'update': "Change all fields in a video report",
        'partial_update': "Change some fields in a video report"}

    KWARGS_DICT = {
        'retrieve': {
            'responses': {
                404: None,
                200: VideoReportsSerializerV2}},
        'update': {
            'responses': {
                404: None,
                201: VideoReportsSerializerV2,
                200: VideoReportsSerializerV2,
                400: None}},
        'partial_update': {
            'responses': {
                404: None,
                201: VideoReportsSerializerV2,
                200: VideoReportsSerializerV2,
                400: None}},
        'create': {
            'responses': {
                400: None,
                201: VideoReportsSerializerV2}},
        'list': {
            'responses': {
                400: None,
                200: VideoReportsSerializerV2(many=True),
            }
        }
    }

    queryset = VideoReports.objects.all()
    serializer_class = VideoReportsSerializerV2
    filterset_class = VideoReportsFilterV2

    def perform_update(self, serializer):
        # setting the user automatically
        with transaction.atomic():
            try:
                serializer.save(user=get_user_preferences(self.request))
            except IntegrityError:
                raise serializers.ValidationError({'detail': "Report already exists"})
            except Exception as e:
                logging.error(e)

    def perform_create(self, serializer):
        # setting the user automatically
        with transaction.atomic():
            try:
                serializer.save(user=get_user_preferences(self.request))
            except IntegrityError:
                raise serializers.ValidationError({'detail': "Report already exists"})
            except Exception as e:
                logging.error(e)
