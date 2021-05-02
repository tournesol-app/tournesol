from collections import OrderedDict
from functools import partial

import django_filters
import numpy as np
from annoying.functions import get_object_or_None
from backend.api_v2.helpers import get_user_preferences, filter_date_ago, identity, \
    WithUpdatedDocstringsDecorator, WithPKOverflowProtection,\
    update_preferences_vector_from_request
from backend.models import Video, UserPreferences, RepresentativeModelUsage,\
    VideoRatingThankYou, UserInformation, VideoRatingPrivacy, VideoRating
from backend.rating_fields import VIDEO_FIELDS, VIDEO_FIELDS_DICT
from backend.video_search import VideoSearchEngine
from backend.youtube_search import search_yt_intersect_tournesol
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.core.exceptions import PermissionDenied
from django.db import connection
from django.db.models import Q, F, Count, Value, FloatField, IntegerField, Case, When
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter, \
    extend_schema_field, inline_serializer
from rest_framework import filters as filters_
from rest_framework import mixins
from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from functools import reduce
from math import isinf
from backend.constants import fields as constants


# number of public contributors to show
N_PUBLIC_CONTRIBUTORS_SHOW = 10


def search_username_from_request(request):
    """Get the username to use the scores from."""
    if not hasattr(request, 'query_params'):
        return False
    if not isinstance(request.query_params, dict):
        return False

    username = request.query_params.get('search_model', None)
    if username:
        qs = VideoRating.objects.filter(user__user__username=username)
        qs = VideoRatingPrivacy._annotate_privacy(qs=qs)
        qs = qs.filter(_is_public=True)
        n_public_videos = qs.count()
        if username != request.user.username and n_public_videos == 0:
            raise PermissionDenied()
        return username
    return False


class UserInformationSerializerNameOnly(serializers.HyperlinkedModelSerializer):
    """Only show username of the person."""

    username = serializers.SerializerMethodField(read_only=True,
                                                 help_text="Username of the contributor",)

    @extend_schema_field(OpenApiTypes.STR)
    def get_username(self, user_information):
        return user_information.user.username

    class Meta:
        model = UserInformation
        fields = ['username']


class VideoSerializerV2(serializers.HyperlinkedModelSerializer):
    """Serialize Videos."""

    # removing enum values not to blow up the openapi spec
    language = serializers.CharField(
        max_length=3,
        help_text="Language as str.",
        read_only=True,
        allow_null=True)
    score = serializers.FloatField(
        help_text="Computed video score.",
        default=0,
        read_only=True,
        allow_null=True)
    tournesol_score = serializers.FloatField(
        help_text=f"The total Tournesol score with uniform preferences "
                  f"(value={constants['DEFAULT_PREFS_VAL']})",
        default=0,
        read_only=True,
        allow_null=True)
    score_preferences_term = serializers.FloatField(
        help_text="Computed video score [preferences].",
        default=0,
        read_only=True,
        allow_null=True)
    score_search_term = serializers.FloatField(
        help_text="Computed video score [search].",
        default=0,
        read_only=True,
        allow_null=True)
    rating_n_experts = serializers.IntegerField(
        help_text="Number of experts in ratings", read_only=True)
    rating_n_ratings = serializers.IntegerField(
        help_text="Number of ratings", read_only=True)
    n_reports = serializers.IntegerField(
        help_text="Number of times video was reported", read_only=True)
    duration = serializers.DurationField(
        help_text="Video Duration",
        allow_null=True,
        read_only=True)
    publication_date = serializers.DateField(
        help_text="When the video was published",
        allow_null=True,
        read_only=True)

    public_experts = serializers.SerializerMethodField(
        help_text=f"First {N_PUBLIC_CONTRIBUTORS_SHOW} public contributors",
        read_only=True)
    n_public_experts = serializers.SerializerMethodField(
        help_text="Number of public contributors", read_only=True)

    n_private_experts = serializers.SerializerMethodField(
        help_text="Number private contributors", read_only=True)

    pareto_optimal = serializers.BooleanField(help_text="Is this video pareto-optimal?",
                                              read_only=True)

    def get_video_object(self, video):
        """Get the video object from ID."""
        if isinstance(video, dict):
            return get_object_or_None(Video, id=video.get('id', -1))
        else:
            return video

    def get_top_raters(self, video):
        video_obj = self.get_video_object(video)
        request = self.context.get("request", {})
        username = search_username_from_request(request)
        if not video_obj:
            qs = UserInformation.objects.none()
        elif username:
            qs = UserInformation.objects.filter(user__username=username)
        else:
            qs = video_obj.certified_top_raters()

        # annotating with whether the rating is public
        pref_privacy = 'user__userpreferences__videoratingprivacy'

        qs = VideoRatingPrivacy._annotate_privacy(
            qs=qs, prefix=pref_privacy,
            field_user=None, filter_add={f'{pref_privacy}__video': video_obj}
        )

        qs = qs.annotate(n_public_rating=Case(
                When(_is_public=True,
                     then=Value(1)),
                default=Value(0),
                output_field=IntegerField()))

        return qs

    FILTER_PUBLIC = Q(n_public_rating=1,
                      show_my_profile=True)

    @extend_schema_field(UserInformationSerializerNameOnly(many=True))
    def get_public_experts(self, video):
        qs = self.get_top_raters(video).filter(self.FILTER_PUBLIC)[
             :N_PUBLIC_CONTRIBUTORS_SHOW]
        s = UserInformationSerializerNameOnly(qs, many=True)
        return s.data

    @extend_schema_field(OpenApiTypes.INT)
    def get_n_public_experts(self, video):
        return self.get_top_raters(video).filter(self.FILTER_PUBLIC).count()

    @extend_schema_field(OpenApiTypes.INT)
    def get_n_private_experts(self, video):
        return self.get_top_raters(video).filter(~self.FILTER_PUBLIC).count()

    def to_representation(self, obj):
        """Adding missing fields because of .values() in queryset"""
        # TODO do not use values and use a raw sql query instead?
        ret = super(VideoSerializerV2, self).to_representation(obj)
        try:
            # restoring fields that are not present because of values()
            v = Video.objects.get(id=ret.get('id', -1))
            for f in set(self.Meta.fields).difference(ret.keys()):
                ret[f] = getattr(v, f)

            if isinf(ret['score_preferences_term']):
                ret['score_preferences_term'] = None
            if isinf(ret['score']):
                ret['score'] = None

            ret = OrderedDict([(key, ret[key]) for key in self.Meta.fields])

        except Video.DoesNotExist:
            pass
        return ret

    class Meta:
        model = Video
        fields = [
            'id',
            'video_id',
            'score',
            'name',
            'duration',
            'language',
            'publication_date',
            'views',
            'uploader',
            'score_preferences_term',
            'score_search_term',
            'rating_n_experts',
            'rating_n_ratings',
            'n_reports',
            'public_experts',
            'n_public_experts',
            'n_private_experts',
            'pareto_optimal',
            'tournesol_score'] + VIDEO_FIELDS
        read_only_fields = [x for x in fields if x != 'video_id']
        extra_kwargs = {'views': {'allow_null': True},
                        'duration': {'allow_null': True},
                        'publication_date': {'allow_null': True},
                        'uploader': {'allow_null': True},
                        'name': {'allow_null': True}}


class VideoFilterV2(filters.FilterSet):
    """Filter videos."""
    days_ago_lte = django_filters.NumberFilter(
        field_name='publication_date',
        method=partial(
            filter_date_ago,
            lookup_expr='gte'),
        label="Upload date, more recent than x days ago",
    )
    days_ago_gte = django_filters.NumberFilter(
        field_name='publication_date',
        method=partial(
            filter_date_ago,
            lookup_expr='lte'),
        label="Upload date, older than x days ago")
    duration_gte = django_filters.DurationFilter(
        field_name='duration', lookup_expr='gte')
    duration_lte = django_filters.DurationFilter(
        field_name='duration', lookup_expr='lte')

    views_gte = django_filters.NumberFilter(
        field_name='views', lookup_expr='gte')
    views_lte = django_filters.NumberFilter(
        field_name='views', lookup_expr='lte')

    language = django_filters.CharFilter(field_name='language')
    search = django_filters.CharFilter(
        field_name="name",
        method=identity,
        label="Search string")
    show_all_my_videos = django_filters.BooleanFilter(
        field_name="video_id",
        method=identity,
        label="Show all my videos in search"
    )

    class Meta:
        model = Video
        fields = [
            'duration_gte',
            'duration_lte',
            'language',
            'video_id',
            'days_ago_gte',
            'days_ago_lte',
            'views_gte',
            'views_lte',
            'search']

    def filter_empty(self, queryset):
        # removing empty videos
        queryset = queryset.exclude(
            name__exact='').exclude(
            score_preferences_term__isnull=True).exclude(
            name__isnull=True).exclude(
            views__exact=0).exclude(
            score__exact=0.0).exclude(
            wrong_url=True).exclude(
            download_failed=True).exclude(
            is_unlisted=True)
        return queryset


@WithUpdatedDocstringsDecorator
class VideoViewSetV2(mixins.CreateModelMixin,
                     mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     WithPKOverflowProtection,
                     viewsets.GenericViewSet, ):
    """Get videos and search results."""

    UPDATE_DOCSTRING = {
        'list': "List all videos with search/filter capability",
        'retrieve': "Get one video by internal ID",
        'create': "Add a video to the database (without filling the fields) from Youtube"}

    # serializers
    VSMany = VideoSerializerV2(many=True)
    VSOne = VideoSerializerV2

    KWARGS_DICT = {
        'create': {
            'responses': {
                400: None, 201: VideoSerializerV2}}, 'retrieve': {
            'responses': {
                404: None, 200: VideoSerializerV2}}, 'list': {
            'responses': {
                200: VSMany, 400: None, 404: None}}}

    queryset = Video.objects.filter(is_unlisted=False)
    serializer_class = VideoSerializerV2
    filter_backends = [filters.DjangoFilterBackend, filters_.OrderingFilter]
    filterset_class = VideoFilterV2
    permission_classes = [IsAuthenticatedOrReadOnly]

    # use Levenstein distance with Elastic search
    search_fields = ['name', 'description', 'uploader']

    # postgres weights https://docs.djangoproject.com/en/3.1/
    # ref/contrib/postgres/search/#weighting-queries
    search_weights = ['A', 'B', 'A']

    assert len(search_fields) == len(search_weights)

    ordering_fields = [
        'name',
        'video_id',
        'views',
        'language',
        'duration',
        'publication_date']

    def get_features_from_request(self):
        """Get preferences features from request, either from the user, or from attributes."""
        # by default, set to zeros
        vector = np.zeros(len(VIDEO_FIELDS))

        # trying to fill data from the user
        try:
            user_prefs = get_user_preferences(self.request)
            vector = user_prefs.features_as_vector_centered
        except UserPreferences.DoesNotExist:
            pass

        vector = update_preferences_vector_from_request(vector, self.request.query_params)

        return vector

    def need_scores_for_username(self):
        return search_username_from_request(self.request)

    def get_queryset(self, pk=None):
        """All videos except for null ones."""
        queryset = Video.objects.filter(is_unlisted=False).values()
        request = self.request

        fields = [x.name for x in Video._meta.fields]
        for f in VIDEO_FIELDS:
            fields.remove(f)

        def get_score_annotation(user_preferences_vector):
            """Returns an sql object annotating queries with the video ratings (sclar product)."""
            return sum(
                [F(f) * v for f, v in zip(VIDEO_FIELDS, user_preferences_vector)])

        features = self.get_features_from_request()
        default_features = [constants['DEFAULT_PREFS_VAL'] for _ in VIDEO_FIELDS]
        search_username = self.need_scores_for_username()

        # computing score inside the database
        if search_username:
            queryset = queryset.values(*fields)
            queryset = queryset.annotate(**{key: F(f'videorating__{key}') for key in VIDEO_FIELDS},
                                         user=F(
                                             'videorating__user__user__username')).filter(
                user=search_username)

            # for myself, allow showing public/non-public videos
            if search_username == request.user.username:
                is_public = request.query_params.get('show_all_my_videos', 'true') == 'false'
                print(is_public)
            else:  # for other people, only show public videos
                is_public = True

            # keeping only public videos
            if is_public:
                queryset = VideoRatingPrivacy._annotate_privacy(
                    queryset, prefix='videoratingprivacy', field_user=None,
                    filter_add={'videoratingprivacy__user__user__username': search_username}
                )
                queryset = queryset.filter(_is_public=True)

            queryset = queryset.annotate(rating_n_experts=Value(1, IntegerField()))

            q1 = Q(expertrating_video_1__user__user__username=search_username)
            q2 = Q(expertrating_video_2__user__user__username=search_username)

            c1 = Count('expertrating_video_1', q1, distinct=True)
            c2 = Count('expertrating_video_2', q2, distinct=True)

            queryset = queryset.annotate(rating_n_ratings=c1 + c2)

            # logging model usage in search
            if self.request.user.is_authenticated:
                RepresentativeModelUsage.objects.get_or_create(
                    viewer=UserPreferences.objects.get(user__username=self.request.user.username),
                    model=UserPreferences.objects.get(user__username=search_username)
                )

        queryset = queryset.annotate(
            score_preferences_term=get_score_annotation(features))

        queryset = queryset.annotate(
            tournesol_score=get_score_annotation(default_features))

        queryset = queryset.annotate(
            score_search_term_=Value(
                0.0, FloatField()))

        if request.query_params.get('search'):
            # computing the postgres score for search
            if connection.vendor.startswith('postgres'):
                s_query = request.query_params.get('search', '')

                def word_to_query(w):
                    """Convert one word into a query."""
                    queries = []

                    queries.append(SearchQuery(w, search_type='raw'))
                    queries.append(SearchQuery(w + ':*', search_type='raw'))

                    return reduce(lambda x, y: x | y, queries)

                def words_to_query(s_query, max_len=100, max_word_len=20):
                    """Convert a string with words into a SearchQuery."""
                    s_query = s_query[:max_len]
                    s_query = s_query.split(' ')
                    s_query = [''.join(filter(str.isalnum, x)) for x in s_query]
                    s_query = [x for x in s_query if 1 <= len(x) <= max_word_len]
                    s_query = [word_to_query(x) for x in s_query]
                    if not s_query:
                        return SearchQuery('')
                    return reduce(lambda x, y: x & y, s_query)

                s_query = words_to_query(s_query)

                s_vectors = [SearchVector(f, weight=w) for f, w in zip(self.search_fields,
                                                                       self.search_weights)]
                s_vector = reduce(lambda x, y: x + y, s_vectors)

                queryset = queryset.annotate(
                    score_search_term_=SearchRank(s_vector, s_query))
            else:
                # in other databases, using basic filtering
                queryset = filters_.SearchFilter().filter_queryset(self.request, queryset, self)
                queryset = queryset.annotate(
                    score_search_term_=Value(
                        1.0, FloatField()))

        queryset = queryset.annotate(
            score_search_term=F('score_search_term_') *
            VideoSearchEngine.VIDEO_SEARCH_COEFF)
        queryset = queryset.annotate(
            score=F('score_preferences_term') +
            F('score_search_term'))

        return queryset

    def return_queryset(self, queryset):
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='search',
                description="Youtube search phrase",
                required=True,
                type=str)],
        responses={
            200: VSMany,
            400: None,
            404: None},
        operation_id="api_v2_video_search_youtube")
    @action(methods=['GET'], detail=False, name="Search using YouTube")
    def search_youtube(self, request):
        """Search videos using the YouTube algorithm."""
        filter = self.filterset_class(request=request)
        queryset = filter.filter_empty(
            self.filter_queryset(
                self.get_queryset()))
        queryset = search_yt_intersect_tournesol(
            request.query_params.get(
                'search', ""), queryset=queryset)
        return self.return_queryset(queryset)

    @extend_schema(operation_id="api_v2_video_search_tournesol",
                   responses={200: VSMany,
                              400: None,
                              403: None,
                              404: None},
                   parameters=[OpenApiParameter(name=k,
                                                description=v + " [preference override]",
                                                required=False,
                                                type=float) for k,
                               v in VIDEO_FIELDS_DICT.items()] + [
                       OpenApiParameter(name='search_model',
                                        description="Use this user's algorithmic representative",
                                        required=False,
                                        type=str)])
    @action(methods=['GET'], detail=False, name="Search using Tournesol")
    def search_tournesol(self, request):
        """Search videos using the Tournesol algorithm."""
        filter = self.filterset_class(request=request)
        queryset = self.get_queryset()
        queryset = queryset.order_by('-score')
        queryset = filter.filter_empty(self.filter_queryset(queryset))
        return self.return_queryset(queryset)

    @extend_schema(operation_id="n_thanks",
                   responses={200: inline_serializer(
                       "NumberOfThanks", {'n_thanks': serializers.IntegerField(
                           required=True,
                           help_text="Number of people I thanked for this video")}),
                              400: None,
                              404: None},
                   parameters=[OpenApiParameter(name="video_id",
                                                description="Youtube Video ID",
                                                required=True,
                                                type=str)])
    @action(methods=['GET'], detail=False, name="Get number of people I thanked for a video")
    def n_thanks(self, request):
        """Get number of people I thanked for a video."""

        video = get_object_or_404(Video, video_id=request.query_params.get('video_id', ''))
        user = get_object_or_404(UserPreferences, user__username=request.user.username)

        n_thanks = VideoRatingThankYou.objects.filter(thanks_from=user,
                                                      video=video).count()
        return Response({'n_thanks': n_thanks}, status=200)

    @extend_schema(operation_id="my_ratings_are_private",
                   responses={200: inline_serializer(
                       "PrivateOrPublic", {'my_ratings_are_private': serializers.BooleanField(
                           required=True,
                           help_text="Are my ratings private?"),
                        'entry_found': serializers.BooleanField(
                               required=True,
                               help_text="Privacy entry found?")
                       }),
                       400: None,
                       404: None},
                   parameters=[OpenApiParameter(name="video_id",
                                                description="Youtube Video ID",
                                                required=True,
                                                type=str)])
    @action(methods=['GET'], detail=False, name="Are my ratings private?")
    def my_ratings_are_private(self, request):
        """Are my ratings private?"""

        video = get_object_or_404(Video, video_id=request.query_params.get('video_id', ''))
        user = get_object_or_404(UserPreferences, user__username=request.user.username)

        qs = VideoRatingPrivacy.objects.filter(user=user,
                                               video=video)

        if qs.count():
            value = qs.get().is_public
        else:
            value = VideoRatingPrivacy.DEFAULT_VALUE_IS_PUBLIC

        return Response({'my_ratings_are_private': not value,
                         'entry_found': qs.count() > 0},
                        status=200)

    # possible actions for thnk_contributors
    thank_actions = ['thank', 'unthank']

    @extend_schema(operation_id="thank_contributors",
                   request=inline_serializer("EmptyThank", fields={}),
                   responses={201: None,
                              400: None,
                              404: None},
                   parameters=[OpenApiParameter(name="video_id",
                                                description="Youtube Video ID",
                                                required=True,
                                                type=str),
                               OpenApiParameter(name="action",
                                                description="Set/unset",
                                                type=str,
                                                required=True,
                                                enum=thank_actions)])
    @action(methods=['PATCH'], detail=False, name="Thank contributors for the video")
    def thank_contributors(self, request):
        """Thank contributors for the video."""

        video = get_object_or_404(Video, video_id=request.query_params.get('video_id', ''))
        action = request.query_params.get('action', "")

        user = get_object_or_404(UserPreferences, user__username=request.user.username)

        if action == 'unthank':
            n_deleted, _ = VideoRatingThankYou.objects.filter(thanks_from=user,
                                                              video=video).delete()
            return Response({'status': 'deleted', 'n_deleted': n_deleted}, status=201)
        elif action == 'thank':
            qs = UserPreferences.objects.all()

            # only keeping people who rated the video
            qs = qs.annotate(n_video=Count(
                'expertrating', Q(expertrating__video_1=video) | Q(expertrating__video_2=video)))
            qs = qs.filter(n_video__gte=1)

            # and who are certified
            qs = UserInformation._annotate_is_certified(qs, prefix="user__userinformation__")
            qs = qs.filter(_is_certified=True)

            # removing yourself...
            qs = qs.exclude(id=user.id)

            contributors = qs.distinct()

            entries = [VideoRatingThankYou(thanks_from=user,
                                           video=video,
                                           thanks_to=contributor)
                       for contributor in contributors]
            VideoRatingThankYou.objects.bulk_create(entries, ignore_conflicts=True)
        else:
            return Response({'reason': f'Wrong action [{action}]'}, status=400)

        return Response({'status': 'success'}, status=201)

    @extend_schema(operation_id="set_rating_privacy",
                   request=inline_serializer("EmptySetPrivacy", {}),
                   responses={201: None,
                              400: None,
                              404: None},
                   parameters=[OpenApiParameter(name="video_id",
                                                description="Youtube Video ID",
                                                required=True,
                                                type=str),
                               OpenApiParameter(name="is_public",
                                                description="Should the rating be public",
                                                required=True,
                                                type=bool)])
    @action(methods=['PATCH'], detail=False, name="Set video rating privacy")
    def set_rating_privacy(self, request):
        """Set video rating privacy."""

        video = get_object_or_404(Video, video_id=request.query_params.get('video_id', ''))
        user = get_object_or_404(UserPreferences, user__username=request.user.username)

        obj, _ = VideoRatingPrivacy.objects.get_or_create(user=user, video=video)
        obj.is_public = request.query_params.get('is_public', 'true') == 'true'
        obj.save()

        return Response({'status': 'success',
                         'is_public': obj.is_public}, status=201)

    @extend_schema(operation_id="set_all_rating_privacy",
                   request=inline_serializer("EmptySetAllPrivacy", {}),
                   responses={201: None,
                              400: None,
                              404: None},
                   parameters=[OpenApiParameter(name="is_public",
                                                description="Should all ratings be public",
                                                required=True,
                                                type=bool)])
    @action(methods=['PATCH'], detail=False, name="Set all video rating privacy")
    def set_all_rating_privacy(self, request):
        """Set all video rating privacy."""

        user = get_object_or_404(UserPreferences, user__username=request.user.username)

        # videos rated by the user
        videos = Video.objects.filter(
            Q(expertrating_video_1__user=user) | Q(expertrating_video_2__user=user)).distinct()

        # creating privacy objects if they don't exist...
        if videos:
            VideoRatingPrivacy.objects.bulk_create(
                [VideoRatingPrivacy(user=user, video=v) for v in videos],
                ignore_conflicts=True)

        is_public = request.query_params.get('is_public', 'true') == 'true'

        VideoRatingPrivacy.objects.filter(user=user).update(is_public=is_public)

        return Response({'status': 'success'}, status=201)
