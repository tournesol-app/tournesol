import logging
from enum import Enum

import gin
import numpy as np
from backend.constants import n_top_popular
from backend.models import VideoRating, Video
from backend.rating_fields import VIDEO_FIELDS
from django.db.models import Q, Sum, F, Func, Count
from django.db.models import Value, FloatField
from django.db.models.functions import Cast
from django.db.models.functions import Coalesce


class ActiveLearningError(Enum):
    """Some errors that can occur when calling functions below."""
    NO_FEATURES = "No features selected as active"
    NO_RATE_LATER_NO_RATED = "Rate later list is empty, and list of rated videos is empty"
    NO_RATE_LATER_ALL_RATED = "Rate later list is empty, and all videos are rated against" \
                              " each other in terms of all quality features"
    FIRST_RATED_AGAINST_ALL_RATED = "First video was rated against all other rated videos"


class ActiveLearningException(Exception):
    """Exception raised on active learning issues."""
    def __init__(self, item):
        self.reason = item
        assert isinstance(item, ActiveLearningError)
        super(ActiveLearningException, self).__init__(item)


def get_active_features(user):
    """Returns a list of features that this user has enabled."""
    return [f for f in VIDEO_FIELDS if getattr(user, f + "_enabled") is True]


def qs_sample_prefetch(qs, n_prefetch=100):
    """Get first items from the queryset, and then sample from the uniform distribution."""
    if not qs:
        raise ValueError("Queryset is empty")
    n_values = len(qs[:n_prefetch])
    idx = np.random.choice(n_values)
    return qs[idx]


def qs_sample_random_order(qs):
    """Annotate with rand() and then sample."""
    if qs.count() == 0:
        raise ValueError("Queryset is empty")

    # order_by('?') does not work with annotate()
    # fix from https://code.djangoproject.com/ticket/26390
    qs = qs.model.objects.filter(id__in=qs)

    return qs.order_by('?').first()


def rate_later_qs(user, base_qs):
    """Get list of videos to rate later by a user."""
    return base_qs.filter(videoratelater__user=user)


def video_rated_by_user(user, base_qs):
    """Only keep videos that have expert ratings by this user."""

    def count_annotation(video_1_or_2):
        """Get number of ratings where this video is video_1_or_2"""
        assert video_1_or_2 in '12', video_1_or_2
        return Count(f'expertrating_video_{video_1_or_2}',
                     filter=Q(**{f'expertrating_video_{video_1_or_2}__user': user}),
                     distinct=True)

    # initial queryset
    qs = base_qs

    # annotating with the number of expert ratings for which the
    # feature f is valid (not None, and weight not 0)
    annotations = {
        f'_r{video_1_or_2}': count_annotation(video_1_or_2)
        for video_1_or_2 in '12'
    }
    qs = qs.annotate(**annotations)

    # annotating with the total (non-unique) number of ratings on this video with valid features
    annotations = {
        '_ratings': sum([F(f'_r{video_1_or_2}')
                         for video_1_or_2 in '12'])
    }

    qs = qs.annotate(**annotations)
    qs = qs.filter(_ratings__gt=0)

    return qs


def video_rated_by_user_filter_not_rated_fully(user, active_features, base_qs,
                                               n_total_override=None, postfix=''):
    """Given an output of video_annotate_num_valid_rating_by_feature(),
    select those that are rated against all videos on all active features."""

    if n_total_override is None:
        # total number of rated videos
        n_total = base_qs.count()
    else:
        n_total = n_total_override

    # we need those that are NOT rated against all other videos (total - 1)
    qs = base_qs.filter(~Q(**{f'_r_all_feature_{f}_valid' + postfix: n_total - 1
                              for f in active_features}))

    return qs


def video_annotate_num_valid_rating_by_feature(user, active_features, base_qs, other_video=None,
                                               postfix=''):
    """Annotate a queryset of videos with the number of valid ratings for each feature.

    Rating can be invalid if:
    1) no ExpertRating entry exist with video=video_1 or video=video_2
    2) some ExpertRating objects exist, but for EVERY active feature EITHER:
      - the weight is 0
      - the rating is None

    if other_video is set, only count ratings where other video is the one specified

    Returns:
        a Queryset of Video objects.
    """

    def count_annotation(video_1_or_2, f):
        """Get the field to annotate videos with the number of ratings
            with a valid feature (not None and weight not 0)."""
        assert video_1_or_2 in '12', video_1_or_2
        video_2_or_1 = '1' if video_1_or_2 == '2' else '2'

        filt = Q(**{f'expertrating_video_{video_1_or_2}__user': user})
        filt = filt & Q(**{f'expertrating_video_{video_1_or_2}__{f}__isnull': False})
        filt = filt & Q(**{f'expertrating_video_{video_1_or_2}__{f}_weight__gt': 0.0})
        if other_video is not None:
            filt = filt & Q(**{f'expertrating_video_{video_1_or_2}__video_{video_2_or_1}__id':
                               other_video.id})

        return Count(f'expertrating_video_{video_1_or_2}', filter=filt, distinct=True)

    # initial queryset
    qs = base_qs

    # annotating with the number of expert ratings for which the
    # feature f is valid (not None, and weight not 0)
    annotations = {
        f'_r{video_1_or_2}_feature_{f}_valid' + postfix:
            count_annotation(video_1_or_2, f)
        for video_1_or_2 in '12'
        for f in active_features
    }
    qs = qs.annotate(**annotations)

    # annotating with the number of ratings
    annotations = {
        f'_r_all_feature_{f}_valid' + postfix:
            F(f'_r1_feature_{f}_valid' + postfix) + F(f'_r2_feature_{f}_valid' + postfix)
        for f in active_features
    }
    qs = qs.annotate(**annotations)

    return qs


def video_no_rating_on_active_features(user, active_features, base_qs):
    """Given an output of video_annotate_num_valid_rating_by_feature(), select videos with
        no valid ratings on active features.

    Returns:
        a Queryset of Video objects.
    """

    # no active features -> don't need to rate
    if not active_features:
        raise ActiveLearningException(ActiveLearningError.NO_FEATURES)

    qs = base_qs

    # annotating with the total (non-unique) number of ratings on this video with valid features
    annotations = {
        '_valid_ratings_sum_features': sum([F(f'_r{video_1_or_2}_feature_{f}_valid')
                                            for video_1_or_2 in '12'
                                            for f in active_features])
    }

    qs = qs.annotate(**annotations)
    qs = qs.filter(_valid_ratings_sum_features=0)

    return qs


def annotate_average_uncertainty(user, active_features, base_qs,
                                 default_value_no_rating=0.0):
    """Given a queryset, annotate with the average (over active features) uncertainty."""

    qs = base_qs

    # default value to be returned if there are no ratings / no active features
    def_value_sql = Value(default_value_no_rating, output_field=FloatField())

    # number of active features
    n_active_sql = Value(len(active_features), output_field=FloatField())

    # no active features -> uncertainty is 0
    if not active_features:
        qs = qs.annotate(_avg_uncertainty_active=def_value_sql)
        return qs

    else:
        # annotating with uncertainty (or 0 if no rating)
        qs = qs.annotate(**{
            f'_uncertainty_{f}': Coalesce(
                Sum(f'videorating__{f}_uncertainty',
                    filter=Q(videorating__user=user)),
                def_value_sql)
            for f in active_features
        })

        # annotating with the average uncertainty over features
        qs = qs.annotate(_avg_uncertainty_active=sum(
            [F(f'_uncertainty_{f}') for f in active_features]) / n_active_sql)

        return qs


@gin.configurable
def sample_first_video_helper(user, do_log=False, base_qs=None):
    """Sample the first video to rate, according to the Overleaf document.

    https://www.overleaf.com/project/5f44dd8e84c8540001bf1552.
    """

    # the base queryset (all Video objects)
    if base_qs is None:
        base_qs = Video.objects.all()

    # ## I. first option -- Rate Later data
    rate_later = rate_later_qs(user, base_qs=base_qs)
    if rate_later.count() > 0:
        if do_log:
            logging.info("Sampling from rate_later")
        return qs_sample_random_order(rate_later)

    # active features
    active_features = get_active_features(user)

    # ## II. second option -- selecting rated videos which have no ratings on active features

    # videos rated by the user, annotated with the number of valid ratings by feature
    v_rated = video_rated_by_user(user, base_qs)
    v_rated_annotate_byf_count = video_annotate_num_valid_rating_by_feature(
        user, active_features, v_rated)

    # out of those, selecting ones which don't have ratings on active features
    v_zero_rating = video_no_rating_on_active_features(user, active_features,
                                                       v_rated_annotate_byf_count)

    if do_log:
        print("List2", v_zero_rating, v_rated)

    if v_zero_rating.count() > 0:
        if do_log:
            logging.info("Sampling from v_zero_rating")
            print("queryset to sample", v_zero_rating)
        res = qs_sample_random_order(v_zero_rating)
        if do_log:
            print("returning", res)
        return res

    if v_rated_annotate_byf_count.count() == 0:
        raise ActiveLearningException(ActiveLearningError.NO_RATE_LATER_NO_RATED)

    # checking that there are no videos rated fully
    not_fully_rated = video_rated_by_user_filter_not_rated_fully(user, active_features,
                                                                 v_rated_annotate_byf_count)
    if not_fully_rated.count() == 0:
        raise ActiveLearningException(ActiveLearningError.NO_RATE_LATER_ALL_RATED)

    # ## III. third option -- selecting the video with highest uncertainty
    # not rated against all others against all quality features
    # adding the average uncertainty
    with_uncertainty = annotate_average_uncertainty(user, active_features,
                                                    not_fully_rated)

    if do_log:
        print("List3", not_fully_rated, with_uncertainty)

    if do_log:
        logging.info("Returning one with highest active uncertainty")
    return with_uncertainty.order_by('-_avg_uncertainty_active').first()


@gin.configurable
def annotate_active_score_with_other_nonoise(v_other, user, active_features, not_fully_rated,
                                             base_qs,
                                             c_exploration=2.0,
                                             c_theta=1.0,
                                             theta_empty_const=1.0, c_skipped=0.1):
    """Implements the active score from Overleaf."""

    if not active_features:
        raise ActiveLearningException(ActiveLearningError.NO_FEATURES)

    qs = base_qs

    def annotate_theta_part(qs, v_other, user, active_features):
        """Compute the theta part of the rating."""
        v_other_my_rating = VideoRating.objects.filter(user=user, video=v_other)
        theta_default_sql = Value(theta_empty_const, FloatField())
        n_features_sql = Cast(len(active_features), output_field=FloatField())

        # rating values cannot be None, so if the entry exists, all the values are valid

        # do NOT have my rating for v_other -> all have a constant penalty
        if v_other_my_rating.count() == 0:
            qs = qs.annotate(_theta_part=theta_default_sql)
        else:
            v_other_my_rating = v_other_my_rating.get()

            # get my ratings for all videos
            annotate_myrating = {
                "my_" + f: Sum('videorating__' + f, videorating__user=user)
                for f in active_features
            }
            qs = qs.annotate(**annotate_myrating)

            # difference to other (or None)
            annotate_diff = {
                "diff_my_" + f: F('my_' + f) - Value(getattr(v_other_my_rating, f),
                                                     output_field=FloatField())
                for f in active_features
            }
            qs = qs.annotate(**annotate_diff)

            # absolute value (or default value)
            annotate_abs = {
                "abs_my_" + f: Coalesce(Func(F('diff_my_' + f), function='ABS'), theta_default_sql)
                for f in active_features
            }
            qs = qs.annotate(**annotate_abs)

            # summing all the differences (l1 norm)
            annotate_abs_sum = {
                "abs_my": sum([F("abs_my_" + f) for f in active_features])
            }
            qs = qs.annotate(**annotate_abs_sum)

            # assigning default value and dividing by number of active features
            val_or_default = {
                "_theta_part": Coalesce(F('abs_my'), theta_default_sql) / n_features_sql
            }
            qs = qs.annotate(**val_or_default)
        return qs

    def annotate_skipped_part(user, qs):
        """Compute the skipped part."""
        # computing number of skips
        skipped = {
            "_skipped_part": Cast(Count('skips', user=user), FloatField())
        }
        qs = qs.annotate(**skipped)
        return qs

    def compute_exploration_part(user, qs):
        """Compute exploration."""
        n_features_sql = Cast(len(active_features), output_field=FloatField())
        qs = qs.annotate(_n_ratings_byf=sum(
            [F(f'_r_all_feature_{f}_valid') for f in active_features]))

        qs = qs.annotate(_exploration_part=n_features_sql / Cast(F('_n_ratings_byf'),
                                                                 output_field=FloatField()))
        return qs

    qs = annotate_theta_part(qs, v_other, user, active_features)
    qs = annotate_skipped_part(user, qs)
    qs = compute_exploration_part(user, qs)

    metric = c_theta * F('_theta_part')
    metric += c_skipped * F('_skipped_part')
    metric += c_exploration * F('_exploration_part')

    qs = qs.annotate(metric_nonoise=metric)
    return qs


@gin.configurable
def subsample_and_noise_and_sample(qs, c_noise, key='metric_nonoise', subsample=100):
    """Select first elements, then add noise and sample with noise in Numpy."""
    vals = list(qs.order_by(key)[:subsample].values('id', key))

    noise = np.random.randn(len(vals))
    vals = [{**v, 'metric': v['metric_nonoise'] + c_noise * n}
            for (v, n) in zip(vals, noise)]
    vals = sorted(vals, key=lambda x: x['metric'])
    idx = vals[0]['id']
    video = Video.objects.get(id=idx)
    return video


def exclude_already_rated(qs, v_other, user):
    """Exclude items that were already compared to v_other."""
    video_compared_to_other = Video.objects.filter(Q(expertrating_video_1__user=user,
                                                     expertrating_video_1__video_2=v_other)
                                                   | Q(expertrating_video_2__user=user,
                                                       expertrating_video_2__video_1=v_other))
    qs = qs.exclude(pk__in=video_compared_to_other)
    return qs


@gin.configurable
def sample_video_with_other_helper(v_other, user, subsample=100,
                                   c_noise=50.0,
                                   do_log=False,
                                   base_qs=None,
                                   debug_return_qs=False):
    """Sample video using the Active Learning loss based on Overleaf.

    https://www.overleaf.com/project/5f44dd8e84c8540001bf1552.
    """

    # the base queryset (all Video objects)
    if base_qs is None:
        base_qs = Video.objects.all()

    def remove_first(qs):
        """Remove the first video from the queryset."""
        # removing the first video
        qs = qs.exclude(id=v_other.id)
        return qs

    # ## I. first option -- Rate Later data
    rate_later = rate_later_qs(user, base_qs=base_qs)
    rate_later = remove_first(rate_later)
    rate_later = exclude_already_rated(rate_later, v_other, user)
    if rate_later.count() > 0:
        if do_log:
            logging.info("Sampling from rate_later")
        return qs_sample_random_order(rate_later)

    # active features
    active_features = get_active_features(user)

    # ## II. second option -- selecting rated videos which have no ratings on active features

    # videos rated by the user, annotated with the number of valid ratings by feature
    v_rated = video_rated_by_user(user, base_qs)
    v_rated_annotate_byf_count = video_annotate_num_valid_rating_by_feature(
        user, active_features, v_rated)

    # out of those, selecting ones which don't have ratings on active features
    v_zero_rating = video_no_rating_on_active_features(user, active_features,
                                                       v_rated_annotate_byf_count)
    v_zero_rating = remove_first(v_zero_rating)

    if do_log:
        print("List2", v_zero_rating, v_rated)

    if v_zero_rating.count() > 0:
        if do_log:
            logging.info("Sampling from v_zero_rating")
        if do_log:
            print("queryset to sample", v_zero_rating)
        res = qs_sample_random_order(v_zero_rating)
        if do_log:
            print("returning", res)
        return res

    # computing annotations ALSO only for ratings where other video is the first one
    v_rated_annotate_byf_count = video_annotate_num_valid_rating_by_feature(
        user, active_features, v_rated_annotate_byf_count, other_video=v_other,
        postfix='_only_other')

    # checking that there are videos that were not fully compared with the first one
    not_fully_rated = video_rated_by_user_filter_not_rated_fully(user, active_features,
                                                                 v_rated_annotate_byf_count,
                                                                 n_total_override=2,
                                                                 postfix='_only_other')

    if do_log:
        print(not_fully_rated)
    not_fully_rated = remove_first(not_fully_rated)
    not_fully_rated_exclude = exclude_already_rated(not_fully_rated, v_other, user)
    if not_fully_rated_exclude.count() == 0:
        raise ActiveLearningException(ActiveLearningError.FIRST_RATED_AGAINST_ALL_RATED)

    # ## III. third option -- selecting the video with lowest metric
    with_metric = annotate_active_score_with_other_nonoise(v_other, user, active_features,
                                                           not_fully_rated, base_qs=not_fully_rated)
    if do_log:
        print("List3", not_fully_rated, with_metric)

    if debug_return_qs:
        return with_metric

    # sorting and returning the top values
    if do_log:
        logging.info("Returning one with lowest metric")

    with_metric_exclude = exclude_already_rated(with_metric, v_other, user)

    return subsample_and_noise_and_sample(with_metric_exclude, c_noise, key='metric_nonoise')


@gin.configurable
def sample_popular_video_helper(base_qs=None):
    """Select top popular videos and sample from the result."""
    if base_qs is None:
        base_qs = Video.objects.all()

    if base_qs.count() == 0:
        raise ValueError("There are no videos")

    # initial queryset
    qs = base_qs

    # ordering by number of views (popular first)
    qs = qs.order_by('-views')

    # selecting top videos
    qs = qs[:n_top_popular]

    return qs_sample_random_order(qs)
