from backend.api_v2.helpers import get_user_preferences, WithUpdatedDocstringsDecorator, \
    WithPKOverflowProtection
from backend.api_v2.helpers import update_preferences_vector_from_request
from backend.models import VideoRating
from backend.models import VideoRatingPrivacy
from backend.rating_fields import VIDEO_FIELDS
from backend.rating_fields import VIDEO_FIELDS_DICT
from django.db.models import F
from django.db.models import Q, Count, Value, Case, When, CharField, BooleanField
from django_filters import rest_framework as filters
from django_react.get_username import current_user
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.utils import extend_schema_field
from rest_framework import mixins
from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


class VideoRatingsSerializerV2(serializers.HyperlinkedModelSerializer):
    """Serialize VideoRatings."""

    user = serializers.PrimaryKeyRelatedField(read_only=True)
    video = serializers.SlugRelatedField(slug_field="video_id", read_only=True)
    score = serializers.FloatField(read_only=True, required=False, default=0)
    rating_n_ratings = serializers.SerializerMethodField(read_only=True,
                                                         help_text="Number of ratings by me")

    @extend_schema_field(OpenApiTypes.INT)
    def get_rating_n_ratings(self, rating):
        username = current_user().username
        return rating.video.ratings(only_certified=False).filter(
            user__user__username=username).values('id').distinct().count()

    class Meta:
        model = VideoRating
        fields = ['id', 'video', 'user', 'score', 'rating_n_ratings'] + VIDEO_FIELDS


class VideoRatingsStatisticsSerializerV2(serializers.HyperlinkedModelSerializer):
    """Give statistics on video ratings."""

    public_username = serializers.CharField(help_text="The person who left the rating",
                                            allow_null=True, allow_blank=True)
    video = serializers.SlugRelatedField(slug_field="video_id", read_only=True)
    score = serializers.FloatField(read_only=True, required=False, default=0)
    n_comparisons = serializers.IntegerField(
        help_text="Number of all pairwise comparisons for the video by the person")

    class Meta:
        model = VideoRating
        fields = ['id', 'video', 'public_username', 'score', 'n_comparisons'] + VIDEO_FIELDS


class VideoRatingsFilterV2(filters.FilterSet):
    """Filter VideoRatings."""

    class Meta:
        model = VideoRating
        fields = ['video', 'video__video_id']


def get_score_annotation(user_preferences_vector):
    """Returns an sql object annotating queries with the video ratings (sclar product)."""
    return sum(
        [F(f) * v for f, v in zip(VIDEO_FIELDS, user_preferences_vector)])


@WithUpdatedDocstringsDecorator
class VideoRatingsViewSetV2(mixins.RetrieveModelMixin,
                            mixins.ListModelMixin,
                            WithPKOverflowProtection,
                            viewsets.GenericViewSet, ):
    """Get my VideoRatings."""

    UPDATE_DOCSTRING = {
        'list': "Get my video ratings (predictions of my algorithmic representative)",
        'retrieve': "Get one video rating (predictions of my algorithmic representative)"}

    KWARGS_DICT = {
        'retrieve': {
            'responses': {
                404: None, 200: VideoRatingsSerializerV2}}, 'list': {
            'responses': {
                200: VideoRatingsSerializerV2(
                    many=True), 400: None}}}

    queryset = VideoRating.objects.all()
    serializer_class = VideoRatingsSerializerV2
    filterset_class = VideoRatingsFilterV2

    def get_queryset(self, pk=None):
        """Only allow accessing own ratings."""
        user_preferences = get_user_preferences(self.request)
        queryset = VideoRating.objects.filter(user=user_preferences)

        # computing score inside the database
        queryset = queryset.annotate(
            score=get_score_annotation(
                get_user_preferences(
                    self.request).features_as_vector_centered))

        return queryset

    @extend_schema(operation_id="video_rating_statistics",
                   responses={200: VideoRatingsStatisticsSerializerV2(many=True),
                              400: None,
                              403: None,
                              404: None},
                   parameters=[OpenApiParameter(name=k,
                                                description=v + " [preference override]",
                                                required=False,
                                                type=float) for k, v in VIDEO_FIELDS_DICT.items()])
    @action(methods=['GET'], detail=False, name="Get statistical data on video ratings")
    def video_rating_statistics(self, request):
        """Get statistical data on video ratings."""
        qs = VideoRating.objects.all()

        # filtering according to the query parameters
        qs = self.filter_queryset(qs)

        # annotate: total score given the preferences
        vector = get_user_preferences(self.request).features_as_vector_centered
        vector = update_preferences_vector_from_request(vector, self.request.query_params)
        qs = qs.annotate(score=get_score_annotation(vector))

        # annotate: public/private rating
        qs = VideoRatingPrivacy._annotate_privacy(
            qs, prefix='video__videoratingprivacy', field_user=F('user'),
            default_value=None, annotate_bool=True, annotate_n=False)

        # either public, or myself
        qs = qs.annotate(_is_public_or_myself=Case(
            When(_is_public=True, then=Value(True)),
            When(user__user__username=request.user.username, then=Value(True)),
            default=Value(False),
            output_field=BooleanField(),
        ))

        # total number of pairwise comparisons by this video by this user
        qs = qs.annotate(n_cmp_1=Count('video__expertrating_video_1', distinct=True,
                                       filter=Q(video__expertrating_video_1__user=F('user'))))
        qs = qs.annotate(n_cmp_2=Count('video__expertrating_video_2', distinct=True,
                                       filter=Q(video__expertrating_video_2__user=F('user'))))

        qs = qs.annotate(n_comparisons=F('n_cmp_1') + F('n_cmp_2'))

        # annotate: for public ones, give the username, for the rest, give None
        qs = qs.annotate(public_username=Case(
            When(_is_public_or_myself=True,
                 then=F('user__user__username')),
            default=Value(None),
            output_field=CharField()))

        # deterministic ordering
        qs = qs.order_by('pk')

        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = VideoRatingsStatisticsSerializerV2(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = VideoRatingsStatisticsSerializerV2(qs, many=True)
        return Response(serializer.data)
