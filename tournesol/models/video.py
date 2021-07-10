import json
import numpy as np
import uuid
import logging

from django.core.validators import RegexValidator
from django.db import models
from django.db.models import (Q, F, Count, Func, Sum, Value, FloatField, IntegerField, Case, When, fields)
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone

import computed_property
from languages.languages import LANGUAGES
from tqdm.auto import tqdm

from core.models import User
from core.utils.models import (WithFeatures, WithDynamicFields, WithEmbedding, ComputedJsonField, query_or, query_and, EnumList)
from core.utils.constants import youtubeVideoIdRegex,ts_constants
from tournesol.utils import VideoSearchEngine
from settings.settings import CRITERIAS, CRITERIAS_DICT, MAX_VALUE, MAX_FEATURE_WEIGHT


class Video(models.Model, WithFeatures, WithEmbedding):
    """One video."""
    video_id_regex = RegexValidator(youtubeVideoIdRegex,
                                    f'Video ID must match {youtubeVideoIdRegex}')

    video_id = models.CharField(
        max_length=20,
        unique=True,
        help_text=f"Video ID from YouTube URL, matches {youtubeVideoIdRegex}",
        validators=[video_id_regex])
    name = models.CharField(max_length=1000, help_text="Video Title",
                            blank=True)
    description = models.TextField(
        null=True, help_text="Video Description from the web page",
        blank=True)
    caption_text = models.TextField(
        null=True, help_text="Processed video caption (subtitle) text",
        blank=True)
    embedding = models.BinaryField(
        null=True,
        help_text="NumPy array with BERT embedding for caption_text, shape("
                  "EMBEDDING_LEN,)")
    info = models.TextField(
        null=True, blank=True,
        help_text="Additional information (json)")
    duration = models.DurationField(null=True, help_text="Video duration", blank=True)
    language = models.CharField(
        null=True, blank=True,
        max_length=10,
        help_text="Language of the video", choices=LANGUAGES)
    publication_date = models.DateField(
        null=True, help_text="Video publication date", blank=True)
    metadata_timestamp = models.DateTimeField(blank=True,
                                              null=True,
                                              help_text="Timestamp the metadata was uploaded")
    views = models.IntegerField(null=True, help_text="Number of views", blank=True)
    uploader = models.CharField(
        max_length=1000,
        null=True, blank=True,
        help_text="Name of the channel (uploader)")

    add_time = models.DateTimeField(null=True,
                                    auto_now_add=True,
                                    help_text="Time the video was added to Tournesol")
    last_download_time = models.DateTimeField(null=True,
                                              blank=True,
                                              help_text="Last time download of metadata"
                                                        " was attempted")
    wrong_url = models.BooleanField(default=False,
                                    help_text="Is the URL incorrect")
    is_unlisted = models.BooleanField(default=False, help_text="Is the video unlisted")
    download_attempts = models.IntegerField(default=0, help_text="Number of times video"
                                                                 " was downloaded")
    download_failed = models.BooleanField(
        default=False, help_text="Was last download unsuccessful")

    is_update_pending = models.BooleanField(
            default=False,
            help_text="If true, recompute properties"
    )

    # computed in the Video.recompute_pareto(),
    #  called via the manage.py compute_quantile_pareto command
    # should be computed after every ml_train command (see the devops script)
    # SEE also: {feature}_quantile fields (defined below)

    pareto_optimal = models.BooleanField(
        null=False,
        default=False,
        help_text="Is the video pareto-optimal based on aggregated scores?")

    # computed properties, updated via save signals,
    #  or via manage.py recompute_properties manage.py

    COMPUTED_PROPERTIES = ['rating_n_contributors', 'rating_n_ratings',
                           'n_public_contributors', 'n_private_contributors', 'public_contributors']

    # computed via signals AND via recompute_properties command
    rating_n_contributors = computed_property.ComputedIntegerField(
        compute_from='get_rating_n_contributors',
        null=False,
        default=0,
        help_text="Total number of certified contributors who rated the video"
    )

    rating_n_ratings = computed_property.ComputedIntegerField(
        compute_from='get_rating_n_ratings',
        null=False,
        default=0,
        help_text="Total number of pairwise comparisons for this video from certified contributors"
    )

    n_public_contributors = computed_property.ComputedIntegerField(
        compute_from='get_n_public_contributors',
        null=False,
        default=0,
        help_text="Number of certified contributors who rated this video publicly"
    )

    n_private_contributors = computed_property.ComputedIntegerField(
        compute_from='get_n_private_contributors',
        null=False,
        default=0,
        help_text="Number of certified contributors who rated this video privately"
    )

    public_contributors = ComputedJsonField(
        compute_from='get_certified_top_raters_list',
        null=False,
        default=list,
        help_text=f"Top {ts_constants['N_PUBLIC_CONTRIBUTORS_SHOW']} certified public contributor usernames"
    )

    # COMPUTED properties implementation
    # TODO create _annotate_is_certified function
    def get_certified_top_raters(self, add_user__username=None):
        """Get certified raters for this video, sorted by number of comparisons."""

        # logging.warning("get_certified_top_raters")

        if self.id is None:
            return User.objects.none()

        filter_this_video = Q(comparisons__video_1=self) |\
            Q(comparisons__video_2=self)

        qs = User.objects.filter(filter_this_video)
        # qs = User._annotate_is_certified(qs)
        # filter_query = Q(_is_certified=True)
        # if add_user__username:
        #     filter_query = filter_query | Q(user__username=add_user__username)
        # qs = qs.filter(filter_query)
        # qs = qs.annotate(_n_comparisons=Count('user__userpreferences__comparison',
        #                                   filter_this_video))
        qs = qs.distinct()
        # qs = qs.order_by('-_n_comparisons')
        return qs

    # public rating and a public contributor
    FILTER_PUBLIC = Q(n_public_rating=1,
                      show_my_profile=True)

    def get_certified_top_raters_list(
            self, limit=ts_constants['N_PUBLIC_CONTRIBUTORS_SHOW'], only_public=True,
            return_json=True):
        """Compute the top certified public top raters and return JSON."""

        # logging.warning("get_certified_top_raters_list")

        qs = self.get_certified_top_raters()

        if qs.count() > 0:
            # annotating with whether the rating is public
            pref_privacy = 'user__userpreferences__videoratingprivacy'

            qs = ContributorRating._annotate_privacy(
                qs=qs, prefix=pref_privacy,
                field_user=None, filter_add={f'{pref_privacy}__video': self}
            )

            qs = qs.annotate(n_public_rating=Case(
                    When(_is_public=True, then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField()))
        else:
            # dummy value in case if we are creating a video
            qs = qs.annotate(n_public_rating=Value(0, output_field=IntegerField()))

        if only_public:
            qs = qs.filter(self.FILTER_PUBLIC)

        if limit is not None:
            qs = qs[:limit]

        if return_json:
            return json.dumps([{'username': user.user.username} for user in qs])

        return qs

    def get_n_public_contributors(self):
        """Get the number of public certified contributors who rated this video."""

        # logging.warning("get_n_public_contributors")

        return self.get_certified_top_raters_list(
                limit=None, return_json=False, only_public=False).\
            filter(self.FILTER_PUBLIC).count()

    def get_n_private_contributors(self):
        """Get the number of private certified contributors who rated this video."""
        return self.get_certified_top_raters_list(
                limit=None, return_json=False, only_public=False).\
            filter(~self.FILTER_PUBLIC).count()

    def get_rating_n_ratings(self, user=None):
        """Number of associated ratings."""
        if user:
            return Comparison.objects.filter(Q(video_1=self) | Q(video_2=self)).filter(user=user).count()
        return Comparison.objects.filter(Q(video_1=self) | Q(video_2=self)).count()

    def get_rating_n_contributors(self):
        """Number of contributors in ratings."""
        return Comparison.objects.filter(Q(video_1=self) | Q(video_2=self)).order_by("user").distinct("user").count()

    # /COMPUTED properties implementation

    def get_pareto_optimal(self):
        """Compute pareto-optimality in sql. Runs in O(n^2) where n=num videos."""
        f1 = query_and([Q(**{f + "__gte": getattr(self, f)}) for f in CRITERIAS])
        f2 = query_or([Q(**{f + "__gt": getattr(self, f)}) for f in CRITERIAS])

        qs = Video.objects.filter(f1).filter(f2)
        return qs.count() == 0

    @staticmethod
    def get_or_create_with_validation(**kwargs):
        """Get an object or validate data and create."""
        qs = Video.objects.filter(**kwargs)
        if qs.count() == 1:
            return qs.get()
        elif qs.count() > 1:
            raise ValueError("Queryset contains more than one item")
        else:
            video = Video(**kwargs)
            video.full_clean()
            video.save()
            return video

    @property
    def best_text(self, min_len=5):
        """Return caption of present, otherwise description, otherwise title."""
        priorities = [self.caption_text, self.description, self.name]

        # going over all priorities
        for v in priorities:
            # selecting one that exists
            if v is not None and len(v) >= min_len:
                return v
        return None

    @property
    def all_text(self):
        """Return concat of caption, description, title."""
        options = [self.caption_text, self.description, self.name]
        options = filter(lambda x: x is not None, options)
        return ' '.join(options)

    @property
    def short_text(self):
        options = [self.name, self.uploader, self.description]
        options = filter(lambda x: x is not None, options)
        return ' '.join(options)[:100]

    @property
    def score_info(self):
        """Get the individual scores as a dictionary."""
        return self._score_info()

    def _score_info(self):
        """Outputs a total score for this video given a user."""
        scores = VideoSearchEngine.score(
            self.short_text, self.features_as_vector)

        for k, v in zip(CRITERIAS, self.features_as_vector):
            scores[k] = v

        return scores

    def score_fcn(self):
        """Outputs a total score for this video given a user."""
        info = self._score_info()
        return info['preferences_term'] + info['phrase_term']

    # @property
    # def score(self):
    #     """Returns the score given a user."""
    #     return self.score_fcn()

    def __str__(self):
        is_correct = self.name and not self.wrong_url and self.views
        correct_str = 'VALID' if is_correct else 'INVALID'
        return f"{self.video_id}, {correct_str}"

    @property
    def tournesol_score(self):
        # computed by a query
        return 0.0
    # TODO create _annotate_is_certified function
    # def ratings(self, user=None, only_certified=True):
    #     """All associated certified ratings."""
    #     f = Q(video_1=self) | Q(video_2=self)
    #     if user is not None:
    #         f = f & Q(user=user)
    #     qs = Comparison.objects.filter(f)
    #     qs = User._annotate_is_certified(
    #         qs, prefix="user__user__")
    #     if only_certified:
    #         qs = qs.filter(_is_certified=True)
    #     return qs

    @staticmethod
    def recompute_quantiles():
        """Set {f}_quantile attribute for videos."""
        quantiles_by_feature_by_id = {f: {} for f in CRITERIAS}

        # go over all features
        # logging.warning("Computing quantiles...")
        for f in tqdm(CRITERIAS):
            # order by feature (descenting, because using the top quantile)
            qs = Video.objects.filter(**{f + "__isnull": False}).order_by('-' + f)
            quantiles_f = np.linspace(0.0, 1.0, len(qs))
            for i, v in tqdm(enumerate(qs)):
                quantiles_by_feature_by_id[f][v.id] = quantiles_f[i]

        logging.warning("Writing quantiles...")
        video_objects = []
        # TODO: use batched updates with bulk_update
        for v in tqdm(Video.objects.all()):
            for f in CRITERIAS:
                setattr(v, f + "_quantile", quantiles_by_feature_by_id[f].get(v.id, None))
            video_objects.append(v)

        Video.objects.bulk_update(video_objects, batch_size=200,
                                  fields=[f + "_quantile" for f in CRITERIAS])

    @staticmethod
    def recompute_pareto():
        """Compute pareto-optimality."""
        # TODO: use a faster algorithm than O(|rated_videos|^2)

        logging.warning("Computing pareto-optimality...")
        video_objects = []
        for v in tqdm(Video.objects.all()):
            new_pareto = v.get_pareto_optimal()
            if new_pareto != v.pareto_optimal:
                v.pareto_optimal = new_pareto
            video_objects.append(v)

        Video.objects.bulk_update(video_objects, batch_size=200,
                                  fields=['pareto_optimal'])

    @staticmethod
    def recompute_computed_properties(only_pending=False):
        qs = Video.objects.all()

        if only_pending:
            logging.warning("Updating pending videos")
            qs = qs.filter(is_update_pending=True)
        else:
            logging.warning("Updating all videos")

        def process_video(v):
            for f in Video.COMPUTED_PROPERTIES:
                getattr(v, f)
            v.is_update_pending = False
            return v

        video_objects = []
        for v in tqdm(qs):
            # computing new values
            video_objects.append(process_video(v))

        Video.objects.bulk_update(video_objects, batch_size=200,
                                  fields=Video.COMPUTED_PROPERTIES + ['is_update_pending'])

class VideoCriteriaScore(models.Model):
    """Scores per criteria for Videos"""

    video = models.ForeignKey(
        to=Video,
        on_delete=models.CASCADE,
        help_text="Foreign key to the video",
        related_name="criteria_scores"
    )
    criteria = models.TextField(
        max_length=32,
        help_text="Name of the criteria",
        db_index=True,
    )
    score = models.FloatField(
        default=0,
        blank=False,
        help_text="Score of the given criteria",
    )
    uncertainty = models.FloatField(
        default=0,
        blank=False,
        help_text="Uncertainty about the video's score for the given criteria",
    )
    # TODO: ensure that the following works:
    # quantiles are computed in the Video.recompute_quantiles(),
    # called via the manage.py compute_quantile_pareto command
    # should be computed after every ml_train command (see the devops script)
    quantile = models.FloatField(
        default=1.0,
        null=False,
        blank=False,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Top quantile for all rated videos for aggregated scores for the given criteria. 0.0=best, 1.0=worst",
    )

    class Meta:
        unique_together = ['video', 'criteria']

    def __str__(self):
        return f"{self.video}/{self.criteria}/{self.score}"


class VideoRateLater(models.Model):
    """List of videos that a person wants to rate later."""
    user = models.ForeignKey(to=User, on_delete=models.CASCADE,
                             help_text="Person who saves the video", related_name="videoratelaters")
    video = models.ForeignKey(to=Video, on_delete=models.CASCADE,
                              help_text="Video in the rate later list", related_name="videoratelaters")

    datetime_add = models.DateTimeField(auto_now_add=True,
                                        help_text="Time the video was added to the"
                                                  " rate later list",
                                        null=True,
                                        blank=True)

    class Meta:
        unique_together = ['user', 'video']
        ordering = ['user', '-datetime_add']

    def __str__(self):
        return f"{self.user}/{self.video}@{self.datetime_add}"


class ContributorRating(models.Model, WithFeatures):
    """Predictions by individual contributor models."""
    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        help_text="Video being scored", related_name="contributorvideoratings")
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="The contributor", related_name="contributorvideoratings")
    is_public = models.BooleanField(default=False, null=False,
                                    help_text="Should the rating be public?")

    class Meta:
        unique_together = ['user', 'video']

    def __str__(self):
        return "%s on %s" % (self.user, self.video)


class ContributorRatingCriteriaScore(models.Model):
    """Scores per criteria for contributors' algorithmic representatives"""

    contributor_rating = models.ForeignKey(
        to=ContributorRating,
        help_text="Foreign key to the contributor's rating",
        related_name="criteria_scores",
        on_delete=models.CASCADE,
    )
    criteria = models.TextField(
        max_length=32,
        help_text="Name of the criteria",
        db_index=True,
    )
    score = models.FloatField(
        default=0,
        blank=False,
        help_text="Score for the given criteria",
    )
    uncertainty = models.FloatField(
        default=0,
        blank=False,
        help_text="Uncertainty about the video's score for the given criteria",
    )

    class Meta:
        unique_together = ['contributor_rating', 'criteria']

    def __str__(self):
        return f"{self.contributor_rating}/{self.criteria}/{self.score}"


class VideoRatingThankYou(models.Model):
    """Thank you for recommendations."""
    video = models.ForeignKey(Video, on_delete=models.CASCADE,
                              help_text="Video thanked for")
    thanks_from = models.ForeignKey(User, on_delete=models.CASCADE,
                                    help_text="Who thanks for the video",
                                    related_name="thanks_from")
    thanks_to = models.ForeignKey(User, on_delete=models.CASCADE,
                                  help_text="Who receives the thanks",
                                  related_name="thanks_to")

    class Meta:
        unique_together = ['video', 'thanks_from', 'thanks_to']

    def __str__(self):
        return "%s to %s for %s" % (self.thanks_from, self.thanks_to, self.video)


class VideoSelectorSkips(models.Model):
    """Count video being skipped in the Video Selector."""
    user = models.ForeignKey(to=User, on_delete=models.CASCADE,
                             related_name="skipped_videos", null=False,
                             help_text="Person who skips the videos")
    video = models.ForeignKey(to=Video, on_delete=models.CASCADE,
                              related_name="skips", null=False,
                              help_text="Video being skipped")
    datetime_add = models.DateTimeField(auto_now_add=True,
                                        help_text="Time the video was skipped",
                                        null=True,
                                        blank=True)

    def __str__(self):
        return f"{self.user}/{self.video}@{self.datetime_add}"


class Comparison(models.Model, WithFeatures):
    """Rating given by a user."""

    class Meta:
        unique_together = ['user', 'video_1_2_ids_sorted']
        constraints = [
            models.CheckConstraint(check=~Q(video_1=F('video_2')),
                                   name='videos_cannot_be_equal')
        ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comparisons",
        help_text="Contributor (user) who left the rating")
    video_1 = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name='comparisons_video_1',
        help_text="Left video to compare")
    video_2 = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name='comparisons_video_2',
        help_text="Right video to compare")
    duration_ms = models.FloatField(
        null=True,
        default=0,
        help_text="Time it took to rate the videos (in milliseconds)")
    datetime_lastedit = models.DateTimeField(
        help_text="Time the comparison was edited the last time",
        null=True, blank=True,
    )
    datetime_add = models.DateTimeField(
        auto_now_add=True, help_text="Time the comparison was added", null=True, blank=True)
    video_1_2_ids_sorted = computed_property.ComputedCharField(
        compute_from='video_first_second',
        max_length=50,
        default=uuid.uuid1,
        help_text="Sorted pair of video IDs")

    @property
    def video_first_second(self, videos=None):
        """String representing two video IDs in sorted order."""
        if videos is None:
            videos = [self.video_1, self.video_2]

        videos = [x.id for x in videos]
        a, b = min(videos), max(videos)
        b = max(videos)
        return f"{a}_{b}"

    @staticmethod
    def sample_video_to_rate(username, T=1):
        """Get one video to rate, the more rated before, the less p to choose."""

        # annotation: number of comparisons for the video
        annotate_num_comparisons = Count('Comparison_video_1__id', distinct=True) + Count(
            'Comparison_video_2__id', distinct=True
        )

        class Exp(Func):
            """Exponent in sql."""
            function = 'Exp'

        # annotating with number of comparisons
        videos = Video.objects.all().annotate(_num_comparisons=annotate_num_comparisons)
        score_exp_annotate = Exp(-Value(T, FloatField()) * F('_num_comparisons'), output_field=FloatField())

        # adding the exponent
        videos = videos.annotate(_score_exp=score_exp_annotate)

        # statistical total sum
        score_exp_sum = videos.aggregate(
            _score_exp_sum=Sum('_score_exp'))['_score_exp_sum']

        # re-computing by dividing by the total sum
        videos = videos.annotate(
            _score_exp_div=F('_score_exp') / score_exp_sum)

        # choosing a random video ID
        ids, ps = zip(*videos.values_list('id', '_score_exp_div'))
        random_video_id = np.random.choice(ids, p=ps)

        return Video.objects.get(id=random_video_id)

    @staticmethod
    def sample_rated_video(username):
        """Get an already rated video, or a random one."""

        # annotation: number of comparisons for the video by username
        annotate_num_comparisons = Count(
            'Comparison_video_1', filter=Q(
                Comparison_video_1__user__user__username=username)) + Count(
            'Comparison_video_2', filter=Q(
                Comparison_video_2__user__user__username=username))

        # annotating with number of comparisons
        videos = Video.objects.all().annotate(_num_comparisons=annotate_num_comparisons)

        # only selecting those already rated.
        videos = videos.filter(_num_comparisons__gt=0)

        if not videos.count():
            logging.warning("No rated videos, returning a random one")
            videos = Video.objects.all()

        # selecting a random ID
        random_id = np.random.choice([x[0] for x in videos.values_list('id')])

        return Video.objects.get(id=random_id)

    @staticmethod
    def sample_video(username, only_rated=False):
        """Sample video based on parameters."""
        if only_rated:
            video = Comparison.sample_rated_video(username)
        else:
            video = Comparison.sample_video_to_rate(username)
        return video

    def weights_vector(self):
        """How important are the individual scores, according to the rater?"""
        return self._features_as_vector_fcn(suffix="_weight")

    def save(self, *args, **kwargs):
        """Save the object data."""
        if not kwargs.pop('ignore_lastedit', False):
            self.datetime_lastedit = timezone.now()
        if self.pk is None:
            kwargs['force_insert'] = True
        return super().save(*args, **kwargs)

    def __str__(self):
        return "%s [%s/%s]" % (self.user, self.video_1, self.video_2)


class ComparisonCriteriaScore(models.Model):
    """Scores per criteria for comparisons submitted by contributors"""


    comparison = models.ForeignKey(
        to=Comparison,
        help_text="Foreign key to the contributor's comparison",
        related_name="criteria_scores",
        on_delete=models.CASCADE,
    )
    criteria = models.TextField(
        max_length=32,
        help_text="Name of the criteria",
        db_index=True,
    )
    # TODO: currently scores range from [0, 100], update them to range from [-10, 10]
    # and add validation
    score = models.FloatField(
        default=0,
        blank=False,
        help_text="Score for the given comparison",
    )
    # TODO: ask Lê if weights should be in a certain range (maybe always > 0)
    # and add validation if required
    weight = models.FloatField(
        default=0,
        blank=False,
        help_text="Weight of the comparison",
    )

    class Meta:
        unique_together = ['comparison', 'criteria']

    def __str__(self):
        return f"{self.comparison}/{self.criteria}/{self.score}"


class ComparisonSliderChanges(models.Model, WithFeatures, WithDynamicFields):
    """Slider values in time for given videos."""

    user = models.ForeignKey(to=User, on_delete=models.CASCADE,
                             help_text="Person changing the sliders",
                             null=True)

    video_left = models.ForeignKey(to=Video, on_delete=models.CASCADE,
                                   help_text="Left video", related_name="slider_left",
                                   null=True)
    video_right = models.ForeignKey(to=Video, on_delete=models.CASCADE,
                                    help_text="Right video", related_name="slider_right",
                                    null=True)

    datetime = models.DateTimeField(
        auto_now_add=True,
        help_text="Time the values are added",
        null=True, blank=True,
    )

    duration_ms = models.FloatField(
        null=True,
        default=0,
        help_text="Time from page load to this slider value (in milliseconds)")

    context = models.CharField(choices=EnumList("RATE", "DIS", "INC"),
                               max_length=10, default="RATE",
                               help_text="The page where slider change occurs")

    @staticmethod
    def _create_fields():
        """Adding score fields."""
        for field in CRITERIAS:
            ComparisonSliderChanges.add_to_class(
                field,
                models.FloatField(
                    blank=True,
                    null=True,
                    default=None,
                    help_text=CRITERIAS_DICT[field],
                    validators=[
                        MinValueValidator(0.0),
                        MaxValueValidator(MAX_VALUE)]))

    def __str__(self):
        return "%s [%s] %s/%s at %s" % (self.user, self.context,
                                        self.video_left, self.video_right, self.datetime)

# adding dynamic fields
WithDynamicFields.create_all()
