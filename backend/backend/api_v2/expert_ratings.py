import json
import logging
from time import time

from annoying.functions import get_object_or_None
from backend.api_v2.helpers import get_user_preferences, WithUpdatedDocstringsDecorator, \
    change_user_data, WithPKOverflowProtection
from backend.api_v2.videos import VideoSerializerV2, VideoViewSetV2
from backend.constants import n_top_popular
from backend.cycle_preference_inconsistency import inconsistencies_3_for_queryset
from backend.disagreements import disagreements_for_user
from backend.ml_model.preference_aggregation_featureless_online import compute_online_update
from backend.models import ExpertRating, Video, VideoSelectorSkips, UserPreferences, \
    ExpertRatingSliderChanges
from backend.rating_fields import MAX_FEATURE_WEIGHT
from backend.rating_fields import MAX_VALUE
from backend.rating_fields import MAX_VALUE as MAX_RATING
from backend.rating_fields import VIDEO_FIELDS
from backend.sample_video_active_learning import sample_video_with_other_helper, \
    sample_first_video_helper, sample_popular_video_helper, ActiveLearningException, \
    ActiveLearningError
from django.db import transaction
from django.db.models import Q
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiParameter, \
    extend_schema_field
from rest_framework import mixins
from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .error_serializer import error_serializer, error_response
from .helpers import video_get_or_create_verify_raise, GenericErrorSerializer
from .online_update_context_cache import cached_class_instance as online_context_cached, invalidate


class SliderChangeSerializerV2(serializers.HyperlinkedModelSerializer):
    """Serialize ExpertRating slider changes."""
    id = serializers.IntegerField(read_only=True, required=False)
    username = serializers.SerializerMethodField(
        help_text="Username of this user", read_only=True)

    video_left = serializers.SlugRelatedField(
        slug_field="video_id",
        read_only=False,
        queryset=Video.objects.all())
    video_right = serializers.SlugRelatedField(
        slug_field="video_id",
        read_only=False,
        queryset=Video.objects.all())

    class Meta:
        model = ExpertRatingSliderChanges
        fields = ['id', 'username', 'video_left', 'video_right',
                  'duration_ms', 'context'] + VIDEO_FIELDS

    @extend_schema_field(OpenApiTypes.STR)
    def get_username(self, rating):
        return rating.user.username

    def is_valid(self, *args, **kwargs):
        # creating videos if they do not exist
        if 'video_left' in self.initial_data:
            video_get_or_create_verify_raise(video_id=self.initial_data['video_left'],
                                             field='video_left')
        if 'video_right' in self.initial_data:
            video_get_or_create_verify_raise(video_id=self.initial_data['video_right'],
                                             field='video_right')

        return super(SliderChangeSerializerV2, self).is_valid(*args, **kwargs)


class ExpertRatingsSerializerV2(serializers.HyperlinkedModelSerializer):
    """Serialize ExpertRatings."""
    id = serializers.IntegerField(read_only=True, required=False)
    username = serializers.SerializerMethodField(
        help_text="Username of this user", read_only=True)
    video_1 = serializers.SlugRelatedField(
        slug_field="video_id",
        read_only=False,
        queryset=Video.objects.all())
    video_2 = serializers.SlugRelatedField(
        slug_field="video_id",
        read_only=False,
        queryset=Video.objects.all())

    @extend_schema_field(OpenApiTypes.STR)
    def get_username(self, rating):
        return rating.user.username

    class Meta:
        model = ExpertRating
        fields = ['id', 'username', 'video_1', 'video_2', 'duration_ms'] + VIDEO_FIELDS + \
                 [f + '_weight' for f in VIDEO_FIELDS]

    def is_valid(self, *args, **kwargs):
        # creating videos if they do not exist
        if 'video_1' in self.initial_data:
            video_get_or_create_verify_raise(video_id=self.initial_data['video_1'],
                                             field='video_1')
        if 'video_2' in self.initial_data:
            video_get_or_create_verify_raise(video_id=self.initial_data['video_2'],
                                             field='video_2')

        return super(ExpertRatingsSerializerV2, self).is_valid(*args, **kwargs)


class ExpertRatingsFilterV2(filters.FilterSet):
    """Filter ExpertRatings."""

    video_1 = filters.CharFilter(
        field_name='video_1__video_id',
        label="First video in the rating (fixed order)")
    video_2 = filters.CharFilter(
        field_name='video_2__video_id',
        label="Second video in the rating (fixed order)")
    video__video_id = filters.CharFilter(
        method='video_any',
        label="Any video ID (first or second)")

    def video_any(self, qs, field_name, value):
        """Any of the two videos equals to a given one."""
        return qs.filter(Q(**{'video_1__video_id': value}) |
                         Q(**{'video_2__video_id': value}))

    class Meta:
        model = ExpertRating
        fields = ['video_1', 'video_2', 'video__video_id']


class SingleFeatureRating(serializers.Serializer):
    """Serialize single-feature comparisons."""
    id = serializers.IntegerField(required=True,
                                  help_text="ExpertRating id")
    videoA = serializers.CharField(required=True,
                                   help_text="Left video")
    videoB = serializers.CharField(required=True,
                                   help_text="Right video")
    score = serializers.FloatField(required=True,
                                   help_text=f"Value in 0..{MAX_VALUE}")


class InconsistenciesSerializer(serializers.Serializer):
    """Serialize inconsistencies"""
    feature = serializers.CharField(
        help_text="Feature the inconsistency is on")

    comparisons = serializers.ListField(
        child=SingleFeatureRating(),
        help_text="All ratings in a cycle",
        allow_empty=True)

    videos = serializers.ListField(
        child=serializers.CharField(
            help_text="video_id"),
        help_text="All videos in a cycle",
        allow_empty=True)


class DisagreementSerializer(serializers.Serializer):
    """Serialize disagreements between ratings and the representative."""
    feature = serializers.CharField(
        help_text="Feature the inconsistency is on")
    video_1__video_id = serializers.CharField(help_text="Left video", required=True)
    video_2__video_id = serializers.CharField(help_text="Right video", required=True)
    model_score = serializers.FloatField(
        help_text=f"The score that the model gives, in 0..{MAX_VALUE}", required=True)
    rating_score = serializers.FloatField(help_text=f"The score that you gave, in 0..{MAX_VALUE}",
                                          required=True)
    mse_01 = serializers.FloatField(
        help_text="Mean squared error between model and rating scores, in 0-1", required=True)


@WithUpdatedDocstringsDecorator
class ExpertRatingsViewSetV2(mixins.CreateModelMixin,
                             mixins.ListModelMixin,
                             mixins.RetrieveModelMixin,
                             mixins.UpdateModelMixin,
                             WithPKOverflowProtection,
                             viewsets.GenericViewSet, ):
    """Set and get expert ratings."""

    queryset = ExpertRating.objects.all()
    serializer_class = ExpertRatingsSerializerV2
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = ExpertRatingsFilterV2

    UPDATE_DOCSTRING = {'list': "List my own expert ratings",
                        "create": "Rate two videos",
                        "update": "Change all fields in a rating",
                        "partial_update": "Change some fields in a rating"}

    KWARGS_DICT = {
        'create': {
            'responses': {
                400: None,
                201: ExpertRatingsSerializerV2}},
        'update': {
            'responses': {
                400: None,
                404: None,
                201: ExpertRatingsSerializerV2,
                200: ExpertRatingsSerializerV2}},
        'partial_update': {
            'responses': {
                400: None,
                404: None,
                201: ExpertRatingsSerializerV2,
                200: ExpertRatingsSerializerV2}},
        'retrieve': {
            'responses': {
                404: None,
                200: ExpertRatingsSerializerV2}},
        'list': {
            'responses': {
                400: None,
                200: ExpertRatingsSerializerV2(
                    many=True)}}}

    def get_queryset(self, pk=None):
        """All videos except for null ones."""
        queryset = ExpertRating.objects.all()
        return queryset.filter(user=get_user_preferences(self.request))

    @extend_schema(responses={200: InconsistenciesSerializer(many=True),
                              400: GenericErrorSerializer, },
                   operation_id="api_v2_expert_ratings_show_inconsistencies")
    @action(methods=['GET'], detail=False, name="Show inconsistencies.")
    def inconsistencies(self, request):
        """Get inconsistencies in Expert Ratings."""
        try:
            data = inconsistencies_3_for_queryset(
                get_user_preferences(
                    self.request),
                queryset=self.get_queryset())
            return Response({'count': len(data),
                             'next': None,
                             'previous': None,
                             'results': InconsistenciesSerializer(data,
                                                                  many=True).data})
        except Exception:
            return error_response(GenericErrorSerializer)

    @extend_schema(responses=DisagreementSerializer(many=True),
                   operation_id="disagreements")
    @action(methods=['GET'], detail=False, name="Show disagreements between model and ratings.")
    def disagreements(self, request):
        """Get disagreements in Expert Ratings."""
        data = disagreements_for_user(
            get_user_preferences(
                self.request))
        return Response({'count': data['count'],
                         'next': None,
                         'previous': None,
                         'results': DisagreementSerializer(data['results'],
                                                           many=True).data})

    @extend_schema(responses={200: VideoViewSetV2.VSOne,
                              400: GenericErrorSerializer},
                   parameters=[OpenApiParameter(name='only_rated',
                                                description='Only sample videos already '
                                                            'rated by the expert',
                                                required=False,
                                                type=bool)],
                   operation_id="api_v2_expert_ratings_sample_video")
    @action(methods=['GET'], detail=False, name="Sample a video to rate.")
    def sample_video(self, request):
        """Sample a video to rate."""
        if Video.objects.count() == 0:
            return Response(GenericErrorSerializer('NO_VIDEOS').data, status=400)
        only_rated = request.query_params.get("only_rated", "") == "true"
        video = ExpertRating.sample_video(
            request.user.username, only_rated=only_rated)
        return Response(VideoSerializerV2(video).data)

    SampleVideoV3Error = error_serializer('SampleVideoV3', errors=ActiveLearningError)

    @extend_schema(responses={200: VideoViewSetV2.VSOne,
                              404: None,
                              400: SampleVideoV3Error},
                   parameters=[OpenApiParameter(name='video_exclude',
                                                description='Exclude a video ID from consideration',
                                                required=False,
                                                type=str)]
                   )
    @action(methods=['GET'], detail=False, name="(sample v3) Sample the first video.")
    def sample_first_video(self, request):
        """Sample a video to rate."""
        if Video.objects.count() == 0:
            return error_response(self.SampleVideoV3Error, 'NO_VIDEOS')

        user = get_object_or_404(UserPreferences, user__username=request.user.username)

        v_exclude_id = request.query_params.get('video_exclude', None)
        v_exclude = get_object_or_None(Video, video_id=v_exclude_id)

        try:
            qs = Video.objects.all()

            if v_exclude is not None:
                qs = qs.exclude(id=qs.id)

            video = sample_first_video_helper(user=user, base_qs=qs)
        except ActiveLearningException as e:
            return error_response(self.SampleVideoV3Error, e.reason.name)
        except Exception:
            return error_response(self.SampleVideoV3Error)
        return Response(VideoSerializerV2(video).data)

    @extend_schema(responses={200: VideoViewSetV2.VSOne,
                              404: None,
                              400: GenericErrorSerializer},
                   parameters=[OpenApiParameter(name='no_rate_later',
                                                description='Do not show videos'
                                                            ' in rate later list',
                                                required=False,
                                                type=bool)]
                   )
    @action(methods=['GET'], detail=False, name=f"Sample a popular video (top {n_top_popular}).")
    def sample_popular_video(self, request):
        """Sample a popular video."""
        if Video.objects.count() == 0:
            return error_response(GenericErrorSerializer, 'NO_VIDEOS')

        try:
            qs = Video.objects.all()
            if request.query_params.get('no_rate_later', False):
                qs = qs.exclude(videoratelater__user__user__username=request.user.username)
            video = sample_popular_video_helper(base_qs=qs)
        except Exception:
            return error_response(GenericErrorSerializer)
        return Response(VideoSerializerV2(video).data)

    @extend_schema(responses={200: VideoViewSetV2.VSOne,
                              404: None,
                              400: SampleVideoV3Error},
                   parameters=[OpenApiParameter(name='video_other',
                                                description='Other video_id being rated',
                                                required=True,
                                                type=str)])
    @action(methods=['GET'], detail=False, name="(sample v3) Sample a video to rate based"
                                                " on another video using Active Learning.")
    def sample_video_with_other(self, request):
        """Sample a video to rate."""
        if Video.objects.count() == 0:
            return error_response(self.SampleVideoV3Error, 'NO_VIDEOS')
        v_other_id = request.query_params.get('video_other', None)
        user = get_object_or_404(UserPreferences, user__username=request.user.username)
        v_other = get_object_or_404(Video, video_id=v_other_id)

        try:
            video = sample_video_with_other_helper(v_other=v_other, user=user)
        except ActiveLearningException as e:
            return error_response(self.SampleVideoV3Error, e.reason.name)
        except Exception:
            return error_response(self.SampleVideoV3Error)
        # return Response(status=404)
        return Response(VideoSerializerV2(video).data)

    def get_by_video_ids(self, request):
        """Get rating by video IDs."""
        user = get_user_preferences(request)
        v1 = request.query_params.get("video_left", "")
        v2 = request.query_params.get("video_right", "")

        r12 = get_object_or_None(ExpertRating, user=user, video_1__video_id=v1,
                                 video_2__video_id=v2)
        r21 = get_object_or_None(ExpertRating, user=user, video_1__video_id=v2,
                                 video_2__video_id=v1)
        if not any([r12, r21]):
            raise ExpertRating.DoesNotExist("Expert Rating not found")

        r = r12 if r12 else r21
        reverse = False if r12 else True
        return r, reverse

    # left and right videos
    params_lr = [
        OpenApiParameter(
            name='video_left',
            description='Left video (can be either v1 or v2)',
            required=True,
            type=str),
        OpenApiParameter(
            name='video_right',
            description='Right video (can be either v1 or v2)',
            required=True,
            type=str),
    ]

    @extend_schema(
        responses={
            201: ExpertRatingsSerializerV2(
                many=False),
            404: None},
        request=inline_serializer(
            "No body",
            fields={}),
        parameters=[
            *params_lr,
            OpenApiParameter(
                name='feature',
                description='The feature to double down the weight on',
                required=True,
                type=str)],
        operation_id="api_v2_expert_ratings_double_down")
    @action(methods=['PATCH'], detail=False, name="Double down")
    def double_down(self, request):
        """Double the weight of one of the ratings on one of the features."""
        try:
            r, reverse = self.get_by_video_ids(request)
        except ExpertRating.DoesNotExist:
            return Response(status=404)

        f = request.query_params.get('feature', "") + '_weight'
        setattr(r, f, min(MAX_FEATURE_WEIGHT, getattr(r, f) * 2))
        r.save()
        return Response(self.get_serializer(r).data)

    @extend_schema(
        responses={
            201: SliderChangeSerializerV2(many=False),
            404: None,
            400: None},
        request=SliderChangeSerializerV2(many=False),
        operation_id="register_slider_change")
    @action(methods=['POST'], detail=False, name="Register slider value change")
    def register_slider_change(self, request):
        """Register any change in slider values on the rating page."""
        serializer = SliderChangeSerializerV2(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=201)

    @extend_schema(
        responses={
            201: None,
            400: None,
        },
        parameters=[],
        request=inline_serializer("Video", fields={
            'video_id': serializers.CharField(help_text="Video id")}, many=True)
    )
    @action(methods=['PATCH'], detail=False, name="Register a video as skipped")
    def skip_video(self, request):
        print(request)
        print(request.data)

        if isinstance(request.data, list):
            video_ids = request.data
        else:
            video_ids = request.data.get('video_id', [])
        user_preferences = UserPreferences.objects.get(user__username=request.user.username)
        n_created = 0
        n_404 = 0

        for video_id in video_ids:
            video = get_object_or_None(Video, video_id=video_id)
            if video is not None:
                n_created += 1
                VideoSelectorSkips.objects.create(user=user_preferences, video=video)
            else:
                n_404 += 1

        return Response({'created': n_created,
                         'does_not_exist': n_404}, status=201)

    @extend_schema(
        responses={
            200: ExpertRatingsSerializerV2(
                many=False), 201: ExpertRatingsSerializerV2(
                many=False), 404: None, 400: None}, parameters=params_lr + [
            OpenApiParameter(
                name='force_set_ids',
                description='Force set video_1 and video_2 (in DB order -- confusing,'
                            ' disabled by-default)',
                required=False,
                type=bool),
        ])
    @action(methods=['GET', 'PATCH'], detail=False,
            name="Set/Get ratings by video IDs, with reverse order supported.")
    def by_video_ids(self, request):
        """Get/set ratings by video IDs, with reverse order (v1-v2 and v2-v1) supported."""
        try:
            r, reverse = self.get_by_video_ids(request)
        except ExpertRating.DoesNotExist:
            return Response(status=404)

        if request.method == 'GET':
            serializer = self.get_serializer(r)

            # now computing the reverse fields
            if reverse:
                for f in set(VIDEO_FIELDS):
                    if getattr(r, f) is not None:
                        setattr(r, f, MAX_RATING - getattr(r, f))

            return Response(serializer.data)
        if request.method == 'PATCH':
            # disallow changing videos in this mode (it is confusing)
            if request.query_params.get('force_set_ids', 'false') != 'true':
                with change_user_data(request.data):
                    if 'video_1' in request.data:
                        del request.data['video_1']
                    if 'video_2' in request.data:
                        del request.data['video_2']

            # first, checking the original data for validity
            serializer = self.get_serializer(
                r, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)

            # now computing the reverse fields
            if reverse:
                with change_user_data(request.data):
                    for f in set(VIDEO_FIELDS).intersection(
                            request.data.keys()):
                        request.data[f] = MAX_RATING - float(request.data[f])

            serializer = self.get_serializer(
                r, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            return Response(serializer.data)

    @extend_schema(
        request=inline_serializer(
            "OnlineRequestSerializer",
            fields={}),
        responses={
            201: inline_serializer(
                "OnlineResponseSerializer",
                fields={
                    'new_score_left': serializers.FloatField(help_text="New value for my score"
                                                                       " for the left video"),
                    'new_score_right': serializers.FloatField(help_text="New value for my score"
                                                                        " for the right video"),
                    'agg_score_left': serializers.FloatField(help_text="New value for aggregated"
                                                                       " score"
                                                                       " for the left video"),
                    'agg_score_right': serializers.FloatField(help_text="New value for aggregated"
                                                                        " score"
                                                                        " for the right video"),
                    'debug_info': serializers.CharField(help_text="Information from"
                                                                  " the optimizer",
                                                        required=False),
                }),
            404: None, 400: None}, parameters=params_lr + [
            OpenApiParameter(
                name='feature',
                description='The feature to update',
                required=True,
                type=str),
            OpenApiParameter(
                name='new_value',
                description=f'New value for the feature in 0..{MAX_VALUE}',
                required=True,
                type=float),
            OpenApiParameter(
                name='add_debug_info',
                description='Return also a dict with information',
                required=False,
                type=bool)
        ])
    @action(methods=['PATCH', 'GET'], detail=False,
            name="Do online updates on ratings.")
    def online_by_video_ids(self, request):
        """Do online updates on ratings."""
        try:
            r, reverse = self.get_by_video_ids(request)
        except ExpertRating.DoesNotExist:
            return Response({'detail': "Rating not found"}, status=404)

        # field to update
        field = request.query_params.get('feature', '')
        if field not in VIDEO_FIELDS:
            return Response({'detail': f"Wrong feature {field}"}, status=400)

        # new rating value
        new_value = request.query_params.get('new_value', '')
        try:
            new_value = float(new_value)
        except ValueError as e:
            return Response({'detail': str(e)})
        if not isinstance(new_value, float) or new_value < 0 or new_value > 100:
            return Response({'detail': f"Wrong new value: {new_value}"}, status=400)

        # save data?
        add_debug_info = request.query_params.get('add_debug_info', 'false') != 'false'

        # preventing a potential OOM error
        try:
            context = online_context_cached(rating_pk=r.id, field=field)
        except ValueError as e:
            return Response({'detail': str(e)}, status=400)

        cache_age = time() - context['cache_created']
        ctx = context['cache']

        # converting 0..100 to -1, 1
        rating_value = new_value / MAX_VALUE  # 0..1
        rating_value = rating_value - 0.5  # -0.5, 0.5
        rating_value *= 2  # -1, 1
        if reverse:
            rating_value = -rating_value

        result = compute_online_update(rating_value=rating_value,
                                       mb_np_orig=ctx.mb_np,
                                       model_tensor_orig=ctx.model_tensor,
                                       idx_set=ctx.idx_set)

        new_model_tensor = result['new_model_tensor']
        minibatch_sizes = {x: len(y) for x, y in result['new_minibatch'].items()}

        # obtaining scores
        new_score_left = new_model_tensor[ctx.usernames.index(ctx.my_username),
                                          ctx.obj1, 0]
        new_score_right = new_model_tensor[ctx.usernames.index(ctx.my_username),
                                           ctx.obj2, 0]
        agg_score_left = new_model_tensor[-1, ctx.obj1, 0]
        agg_score_right = new_model_tensor[-1, ctx.obj2, 0]

        if reverse:
            (new_score_left, new_score_right) = (new_score_right, new_score_left)
            (agg_score_left, agg_score_right) = (agg_score_right, agg_score_left)

        do_save = request.method == 'PATCH'
        if do_save:
            context['cache'].write_updates_to_db(new_model_tensor)
            invalidate(rating_pk=r.id, field=field)

        data = {'new_score_left': new_score_left,
                'new_score_right': new_score_right,
                'agg_score_left': agg_score_left,
                'agg_score_right': agg_score_right}

        if add_debug_info:
            data['debug_info'] = {
                'cache_age': cache_age,
                'saved': do_save,
                'other_users': len(ctx.usernames) - 1,
                'ratings_in_loss': len(ctx.ratings_selected),
                'videos_in_loss': len(ctx.videos_selected),
                'minibatch_sizes': minibatch_sizes,
            }
            data['debug_info'] = json.dumps(data['debug_info'])

        return Response(data, status=201)

    def perform_create(self, serializer):
        # setting the user automatically
        with transaction.atomic():
            try:
                serializer.save(user=get_user_preferences(self.request))
            except IntegrityError:
                raise serializers.ValidationError({'detail': "Rating exists already"})
            except Exception as e:
                logging.error(e)
