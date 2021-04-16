import datetime
import hashlib

from backend.api_v2.helpers import get_user_preferences, pretty_time_delta, \
    WithUpdatedDocstringsDecorator, WithPKOverflowProtection, HashIDStorage
from backend.models import Video, VideoComment, VideoCommentMarker, EmailDomain
from backend.rating_fields import VIDEO_FIELDS
from django.db.models import Count, Q, F
from django_filters import rest_framework as filters
from django_react.get_username import current_user
from django_react.settings import COMMENT_USERNAME_SALT
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiParameter, \
    extend_schema_field
from rest_framework import mixins
from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
import django_filters


class VideoCommentsSerializerV2(serializers.HyperlinkedModelSerializer):
    """Serialize comments."""
    id = serializers.IntegerField(read_only=True, required=False)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    video = serializers.SlugRelatedField(
        slug_field="video_id",
        read_only=False,
        queryset=Video.objects.all())
    parent_comment = serializers.PrimaryKeyRelatedField(
        read_only=False,
        allow_null=True,
        queryset=VideoComment.objects.all(),
        required=False)
    datetime_add_ago = serializers.SerializerMethodField(
        help_text="Human-readable x time units ago", read_only=True)
    edited_m_added_s = serializers.SerializerMethodField(
        help_text="Edited minus created time in seconds", read_only=True)
    username = serializers.SerializerMethodField(
        help_text="User username", read_only=True, required=False)
    children = serializers.IntegerField(
        help_text="Number of children comments", read_only=True)
    red_flags = serializers.IntegerField(
        help_text="Number of red flags", read_only=True)
    votes_plus = serializers.IntegerField(
        help_text="Number of likes", read_only=True)
    votes_minus = serializers.IntegerField(
        help_text="Number of dislikes", read_only=True)
    # anonymized_username = serializers.SerializerMethodField(
    # help_text="Hash of the usernamee", required=False)
    anonymized_username_id = serializers.SerializerMethodField(
        help_text="ID of the hash of the username", required=False)

    hash_storage = HashIDStorage()

    @extend_schema_field(OpenApiTypes.INT)
    def get_anonymized_username_id(self, comment):
        anon_username = self.get_anonymized_username(comment)
        return self.hash_storage.add(comment.video.video_id, anon_username)

    # @extend_schema_field(OpenApiTypes.STR)

    def get_anonymized_username(self, comment):
        """Get hash of the username."""
        return hashlib.md5(f"{comment.user.username}_{COMMENT_USERNAME_SALT}"
                           .encode('utf-8')).hexdigest()

    def to_representation(self, obj):
        """Removing data dynamically to protect privacy #27."""
        ret = super(VideoCommentsSerializerV2, self).to_representation(obj)
        if current_user().username != obj.user.username:
            if obj.anonymous:
                ret['username'] = ""
                ret['user'] = -1

        return ret

    @extend_schema_field(OpenApiTypes.STR)
    def get_datetime_add_ago(self, comment):
        date = comment.datetime_add.replace(tzinfo=None)
        time_ago = datetime.datetime.now() - date
        time_ago = pretty_time_delta(time_ago.total_seconds())
        return time_ago

    @extend_schema_field(OpenApiTypes.FLOAT)
    def get_edited_m_added_s(self, comment):
        date = comment.datetime_add.replace(tzinfo=None)
        date_edit = comment.datetime_lastedit.replace(tzinfo=None)
        return (date_edit - date).total_seconds()

    @extend_schema_field(OpenApiTypes.STR)
    def get_username(self, comment):
        return comment.user.username

    class Meta:
        model = VideoComment
        fields = [
            'user',
            'video',
            'parent_comment',
            'comment',
            'username',
            'anonymized_username_id',
            'datetime_lastedit',
            'datetime_add',
            'votes_plus',
            'anonymous',
            'votes_minus',
            'red_flags',
            'id',
            'children',
            'datetime_add_ago',
            'edited_m_added_s'] + VIDEO_FIELDS


class VideoCommentsFilterV2(filters.FilterSet):
    """Filter comments."""

    comment = django_filters.CharFilter(lookup_expr='icontains',
                                        help_text="Comment contains text")

    class Meta:
        model = VideoComment
        fields = ['video__video_id', 'parent_comment',
                  'comment', 'user__user__username'] + VIDEO_FIELDS


@WithUpdatedDocstringsDecorator
class VideoCommentsViewSetV2(mixins.RetrieveModelMixin,
                             mixins.ListModelMixin,
                             mixins.CreateModelMixin,
                             mixins.UpdateModelMixin,
                             WithPKOverflowProtection,
                             viewsets.GenericViewSet, ):
    """Post, edit, mark comments."""

    UPDATE_DOCSTRING = {'list': "List and filter comments",
                        'retrieve': "Get one comment",
                        'create': "Comment on a video",
                        'update': "Change all fields in a comment",
                        'partial_update': "Change some fields in a comment"}

    KWARGS_DICT = {
        'create': {
            'responses': {
                400: None,
                201: VideoCommentsSerializerV2}},
        'update': {
            'responses': {
                400: None,
                404: None,
                201: VideoCommentsSerializerV2,
                200: VideoCommentsSerializerV2}},
        'partial_update': {
            'responses': {
                400: None,
                404: None,
                201: VideoCommentsSerializerV2,
                200: VideoCommentsSerializerV2}},
        'retrieve': {
            'responses': {
                404: None,
                200: VideoCommentsSerializerV2}},
        'list': {
            'responses': {
                200: VideoCommentsSerializerV2(
                    many=True),
                400: None}}}

    queryset = VideoComment.objects.all()
    serializer_class = VideoCommentsSerializerV2
    filterset_class = VideoCommentsFilterV2

    def get_queryset(self, pk=None):
        """Adding the proposed metric."""
        queryset = VideoComment.objects.select_related()

        # only selecting comments from certified users, or from me
        queryset = queryset.annotate(
            n_cert_email=Count(
                'user__user__userinformation__emails',
                filter=Q(
                    user__user__userinformation__emails__domain_fk__status=EmailDomain
                    .STATUS_ACCEPTED,
                    user__user__userinformation__emails__is_verified=True)))
        queryset = queryset.filter(
            Q(user__user__username=self.request.user.username) | Q(n_cert_email__gt=0))

        # adding votes
        queryset = queryset.annotate(
            votes_plus_=Count(
                'videocommentmarker_comment', filter=Q(
                    videocommentmarker_comment__which="vote_plus")), votes_minus_=Count(
                'videocommentmarker_comment', filter=Q(
                    videocommentmarker_comment__which="vote_minus")), red_flags_=Count(
                'videocommentmarker_comment', filter=Q(
                    videocommentmarker_comment__which="red_flag")))

        # computing the metric, see #47
        queryset = queryset.annotate(
            sort_metric=(
                F('votes_plus_') *
                1.1 +
                1) /
            (
                1 +
                F('votes_plus_') +
                F('votes_minus_')) -
            VideoComment.red_flag_weight *
            F('red_flags_'))

        return queryset

    # add/delete actions for markers
    marker_actions = ["add", "delete", "toggle"]

    @extend_schema(
        responses={
            201: VideoCommentsSerializerV2(
                many=False),
            400: None,
            422: None,
            404: None},
        parameters=[
            OpenApiParameter(
                name='marker',
                description=f'The marker to set, one of {VideoCommentMarker.MARKER_CHOICES_1}',
                required=True,
                type=str,
                enum=VideoCommentMarker.MARKER_CHOICES_1),
            OpenApiParameter(
                name='action',
                description=f'Delete or add the marker, one of {marker_actions}',
                required=True,
                type=str,
                enum=marker_actions),
        ],
        request=inline_serializer(
            name="Empty",
            fields={}),
        operation_id="api_v2_video_comments_set_mark")
    @action(methods=['POST'], detail=True, name="Set markers")
    def set_mark(self, request, pk=None):
        """Mark a comment with a flag (like/dislike/red flag)."""
        fields = VideoCommentMarker.MARKER_CHOICES_1

        if request.query_params.get('marker', "") not in fields:
            return Response(
                status=400, data={
                    'explanation': f"Marker must be one of {fields}"})
        if request.query_params.get("action", "") not in self.marker_actions:
            return Response(
                status=400, data={
                    'explanation': f"Action must be one of {self.marker_actions}"})

        f = request.query_params['marker']
        action_ = request.query_params['action']

        f0 = VideoCommentMarker.MARKER_CHOICES_1to0[f]

        if not self.get_queryset().filter(id=pk).count():
            return Response(status=404)

        c = self.get_object()
        marker_user = get_user_preferences(request)

        kwargs = dict(comment=c, which=f0, user=marker_user)

        if action_ == "delete" and not VideoCommentMarker.objects.filter(
                **kwargs).count():
            return Response(
                status=422, data={
                    'explanation': "Cannot delete, marker does not exist"})
        if action_ == "add" and VideoCommentMarker.objects.filter(
                **kwargs).count():
            return Response(
                status=422, data={
                    'explanation': "Cannot add, marker already exists"})

        if action_ == "add":
            VideoCommentMarker.objects.create(**kwargs).save()
        elif action_ == "delete":
            VideoCommentMarker.objects.filter(**kwargs).delete()
        elif action_ == "toggle":
            n_now = VideoCommentMarker.objects.filter(**kwargs).count()
            if n_now:
                VideoCommentMarker.objects.filter(**kwargs).delete()
            else:
                VideoCommentMarker.objects.create(**kwargs).save()

        return Response(self.get_serializer(c, many=False).data, status=201)

    def filter_queryset(self, queryset):
        queryset = super(
            VideoCommentsViewSetV2,
            self).filter_queryset(queryset)
        return queryset.order_by('-sort_metric')

    def perform_create(self, serializer):
        serializer.save(user=get_user_preferences(self.request))

    def perform_update(self, serializer):
        serializer.save(user=get_user_preferences(self.request))
