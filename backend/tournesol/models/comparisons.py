"""
Models for Tournesol's main functions related to contributor's comparisons
"""

import uuid
import logging
import numpy as np

from django.db import models
from django.db.models import (
    ObjectDoesNotExist,
    Q,
    F,
    Count,
)
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone

import computed_property

from core.models import User
from core.utils.models import (
    WithFeatures,
    WithDynamicFields,
    enum_list,
)
from settings.settings import CRITERIAS, CRITERIAS_DICT, MAX_VALUE


class Comparison(models.Model, WithFeatures):
    """Rating given by a user."""

    class Meta:
        unique_together = ["user", "video_1_2_ids_sorted"]
        constraints = [
            models.CheckConstraint(
                check=~Q(video_1=F("video_2")), name="videos_cannot_be_equal"
            )
        ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comparisons",
        help_text="Contributor (user) who left the rating",
    )
    video_1 = models.ForeignKey(
        'Video',
        on_delete=models.CASCADE,
        related_name="comparisons_video_1",
        help_text="Left video to compare",
    )
    video_2 = models.ForeignKey(
        'Video',
        on_delete=models.CASCADE,
        related_name="comparisons_video_2",
        help_text="Right video to compare",
    )
    duration_ms = models.FloatField(
        null=True,
        default=0,
        help_text="Time it took to rate the videos (in milliseconds)",
    )
    datetime_lastedit = models.DateTimeField(
        help_text="Time the comparison was edited the last time",
        null=True,
        blank=True,
        auto_now=True,
    )
    datetime_add = models.DateTimeField(
        auto_now_add=True,
        help_text="Time the comparison was added",
        null=True,
        blank=True,
    )
    video_1_2_ids_sorted = computed_property.ComputedCharField(
        compute_from="video_first_second",
        max_length=50,
        default=uuid.uuid1,
        help_text="Sorted pair of video IDs",
    )

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
    def get_comparison(user, video_id_1, video_id_2):
        """
        Return a tuple with the user's comparison between two videos, and
        True is the comparison is made in the reverse way, False instead.

        Raise django.db.model.ObjectDoesNotExist if no comparison is found.
        """
        try:
            comparison = Comparison.objects.get(
                video_1__video_id=video_id_1,
                video_2__video_id=video_id_2,
                user=user
            )
        except ObjectDoesNotExist:
            pass
        else:
            return comparison, False

        comparison = Comparison.objects.get(
            video_1__video_id=video_id_2,
            video_2__video_id=video_id_1,
            user=user
        )

        return comparison, True

    @staticmethod
    def sample_video_to_rate(username, rated_count=1):
        """Get one video to rate, the more rated before, the less probable to choose."""
        # TODO: re-enable sampling videos for rating

        # # annotation: number of comparisons for the video
        # annotate_num_comparisons = Count(
        #     "Comparison_video_1__id", distinct=True
        # ) + Count("Comparison_video_2__id", distinct=True)

        # class Exp(Func):
        #     """Exponent in sql."""

        #     function = "Exp"

        # # annotating with number of comparisons
        # videos = Video.objects.all().annotate(_num_comparisons=annotate_num_comparisons)
        # score_exp_annotate = Exp(
        #     -Value(rated_count, FloatField()) * F("_num_comparisons"), output_field=FloatField()
        # )

        # # adding the exponent
        # videos = videos.annotate(_score_exp=score_exp_annotate)

        # # statistical total sum
        # score_exp_sum = videos.aggregate(_score_exp_sum=Sum("_score_exp"))[
        #     "_score_exp_sum"
        # ]

        # # re-computing by dividing by the total sum
        # videos = videos.annotate(_score_exp_div=F("_score_exp") / score_exp_sum)

        # # choosing a random video ID
        # ids, scores = zip(*videos.values_list("id", "_score_exp_div"))
        # random_video_id = np.random.choice(ids, p=scores)

        # return Video.objects.get(id=random_video_id)

        return None

    @staticmethod
    def sample_rated_video(username):
        """Get an already rated video, or a random one."""
        from .video import Video

        # annotation: number of comparisons for the video by username
        annotate_num_comparisons = Count(
            "Comparison_video_1",
            filter=Q(Comparison_video_1__user__user__username=username),
        ) + Count(
            "Comparison_video_2",
            filter=Q(Comparison_video_2__user__user__username=username),
        )

        # annotating with number of comparisons
        videos = Video.objects.all().annotate(_num_comparisons=annotate_num_comparisons)

        # only selecting those already rated.
        videos = videos.filter(_num_comparisons__gt=0)

        if not videos.count():
            logging.warning("No rated videos, returning a random one")
            videos = Video.objects.all()

        # selecting a random ID
        random_id = np.random.choice([x[0] for x in videos.values_list("id")])

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
        if not kwargs.pop("ignore_lastedit", False):
            self.datetime_lastedit = timezone.now()
        if self.pk is None:
            kwargs["force_insert"] = True
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
        help_text="Score for the given comparison",
    )
    # TODO: ask Lê if weights should be in a certain range (maybe always > 0)
    # and add validation if required
    weight = models.FloatField(
        default=1,
        blank=False,
        help_text="Weight of the comparison",
    )

    class Meta:
        unique_together = ["comparison", "criteria"]

    def __str__(self):
        return f"{self.comparison}/{self.criteria}/{self.score}"


class ComparisonSliderChanges(models.Model, WithFeatures, WithDynamicFields):
    """Slider values in time for given videos."""

    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        help_text="Person changing the sliders",
        null=True,
    )

    video_left = models.ForeignKey(
        to='Video',
        on_delete=models.CASCADE,
        help_text="Left video",
        related_name="slider_left",
        null=True,
    )
    video_right = models.ForeignKey(
        to='Video',
        on_delete=models.CASCADE,
        help_text="Right video",
        related_name="slider_right",
        null=True,
    )

    datetime = models.DateTimeField(
        auto_now_add=True,
        help_text="Time the values are added",
        null=True,
        blank=True,
    )

    duration_ms = models.FloatField(
        null=True,
        default=0,
        help_text="Time from page load to this slider value (in milliseconds)",
    )

    context = models.CharField(
        choices=enum_list("RATE", "DIS", "INC"),
        max_length=10,
        default="RATE",
        help_text="The page where slider change occurs",
    )

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
                    validators=[MinValueValidator(0.0), MaxValueValidator(MAX_VALUE)],
                ),
            )

    def __str__(self):
        return "%s [%s] %s/%s at %s" % (
            self.user,
            self.context,
            self.video_left,
            self.video_right,
            self.datetime,
        )


# adding dynamic fields
WithDynamicFields.create_all()
