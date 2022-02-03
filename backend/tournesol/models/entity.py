"""
Entity and closed related models.
"""

import logging
from datetime import timedelta

import numpy as np
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.html import format_html
from tqdm.auto import tqdm

from core.models import User
from core.utils.constants import YOUTUBE_VIDEO_ID_REGEX
from core.utils.models import WithEmbedding, WithFeatures, query_and, query_or
from tournesol.models.comparisons import Comparison
from tournesol.models.tags import Tag
from tournesol.utils import VideoSearchEngine

CRITERIAS = settings.CRITERIAS
LANGUAGES = settings.LANGUAGES


class Entity(models.Model, WithFeatures, WithEmbedding):
    """
    A generic entity that can be compared with another one.

    The current model still contains fields from the previous `Video` model.
    These fields are kept as-is for now to ease the refactor of the Tournesol
    app, and will be replaced in the future by the `metadata` JSON field.
    """
    video_id_regex = RegexValidator(
        YOUTUBE_VIDEO_ID_REGEX, f"Video ID must match {YOUTUBE_VIDEO_ID_REGEX}"
    )

    video_id = models.CharField(
        max_length=20,
        unique=True,
        help_text=f"Video ID from YouTube URL, matches {YOUTUBE_VIDEO_ID_REGEX}",
        validators=[video_id_regex],
    )
    name = models.CharField(max_length=1000, help_text="Video Title", blank=True)
    description = models.TextField(
        null=True, help_text="Video Description from the web page", blank=True
    )
    caption_text = models.TextField(
        null=True, help_text="Processed video caption (subtitle) text", blank=True
    )
    embedding = models.BinaryField(
        null=True,
        help_text="NumPy array with BERT embedding for caption_text, shape("
        "EMBEDDING_LEN,)",
    )
    info = models.TextField(
        null=True, blank=True, help_text="Additional information (json)"
    )
    duration = models.DurationField(null=True, help_text="Video duration", blank=True)
    language = models.CharField(
        null=True,
        blank=True,
        max_length=10,
        help_text="Language of the video",
        choices=LANGUAGES,
    )
    publication_date = models.DateField(
        null=True, help_text="Video publication date", blank=True
    )
    metadata_timestamp = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Timestamp the metadata was uploaded",
    )
    views = models.BigIntegerField(null=True, help_text="Number of views", blank=True)
    uploader = models.CharField(
        max_length=1000,
        null=True,
        blank=True,
        help_text="Name of the channel (uploader)",
    )

    add_time = models.DateTimeField(
        null=True, auto_now_add=True, help_text="Time the video was added to Tournesol"
    )
    last_metadata_request_at = models.DateTimeField(
        null=True,
        blank=True,
        auto_now_add=True,
        help_text="Last time fetch of metadata was attempted",
    )
    wrong_url = models.BooleanField(default=False, help_text="Is the URL incorrect")
    is_unlisted = models.BooleanField(default=False, help_text="Is the video unlisted")

    tags = models.ManyToManyField(Tag, blank=True)

    # computed in the Entity.recompute_pareto(),
    #  called via the manage.py compute_quantile_pareto command
    # should be computed after every ml_train command (see the devops script)
    # SEE also: {feature}_quantile fields (defined below)

    pareto_optimal = models.BooleanField(
        null=False,
        default=False,
        help_text="Is the video pareto-optimal based on aggregated scores?",
    )

    rating_n_ratings = models.IntegerField(
        null=False,
        default=0,
        help_text="Total number of pairwise comparisons for this video"
        "from certified contributors",
    )

    rating_n_contributors = models.IntegerField(
        null=False,
        default=0,
        help_text="Total number of certified contributors who rated the video",
    )

    def update_n_ratings(self):
        self.rating_n_ratings = Comparison.objects.filter(
            Q(video_1=self) | Q(video_2=self)
        ).count()
        self.rating_n_contributors = (
            Comparison.objects.filter(Q(video_1=self) | Q(video_2=self))
            .distinct("user")
            .count()
        )
        self.save(update_fields=["rating_n_ratings", "rating_n_contributors"])

    def get_pareto_optimal(self):
        """Compute pareto-optimality in sql. Runs in O(n^2) where n=num videos."""
        f_1 = query_and([Q(**{f + "__gte": getattr(self, f)}) for f in CRITERIAS])
        f_2 = query_or([Q(**{f + "__gt": getattr(self, f)}) for f in CRITERIAS])

        qs = Entity.objects.filter(f_1).filter(f_2)
        return qs.count() == 0

    @property
    def best_text(self, min_len=5):
        """Return caption of present, otherwise description, otherwise title."""
        priorities = [self.caption_text, self.description, self.name]

        # going over all priorities
        for priority in priorities:
            # selecting one that exists
            if priority is not None and len(priority) >= min_len:
                return priority
        return None

    @property
    def all_text(self):
        """Return concat of caption, description, title."""
        options = [self.caption_text, self.description, self.name]
        options = filter(lambda x: x is not None, options)
        return " ".join(options)

    @property
    def short_text(self):
        """Returns a short string representation of a video"""
        options = [self.name, self.uploader, self.description]
        options = filter(lambda x: x is not None, options)
        return " ".join(options)[:100]

    @property
    def score_info(self):
        """Get the individual scores as a dictionary."""
        return self._score_info()

    def _score_info(self):
        """Outputs a total score for this video given a user."""
        scores = VideoSearchEngine.score(self.short_text, self.features_as_vector)

        for criteria, score_vector in zip(CRITERIAS, self.features_as_vector):
            scores[criteria] = score_vector

        return scores

    def score_fcn(self):
        """Outputs a total score for this video given a user."""
        info = self._score_info()
        return info["preferences_term"] + info["phrase_term"]

    # @property
    # def score(self):
    #     """Returns the score given a user."""
    #     return self.score_fcn()

    def __str__(self):
        return f"{self.video_id}"

    def link_to_youtube(self):
        return format_html(
            '<a href="https://youtu.be/{}" target="_blank">Play ▶</a>', self.video_id
        )

    @property
    def tournesol_score(self):
        """Overall score computed for a video based on aggregated contributions"""
        # computed by a query
        return 0.0

    @staticmethod
    def recompute_quantiles():
        """Set {f}_quantile attribute for videos."""
        quantiles_by_feature_by_id = {f: {} for f in CRITERIAS}

        # go over all features
        # logging.warning("Computing quantiles...")
        for f in tqdm(CRITERIAS):
            # order by feature (descenting, because using the top quantile)
            qs = Entity.objects.filter(**{f + "__isnull": False}).order_by("-" + f)
            quantiles_f = np.linspace(0.0, 1.0, len(qs))
            for i, v in tqdm(enumerate(qs)):
                quantiles_by_feature_by_id[f][v.id] = quantiles_f[i]

        logging.warning("Writing quantiles...")
        video_objects = []
        # TODO: use batched updates with bulk_update
        for v in tqdm(Entity.objects.all()):
            for f in CRITERIAS:
                setattr(
                    v, f + "_quantile", quantiles_by_feature_by_id[f].get(v.id, None)
                )
            video_objects.append(v)

        Entity.objects.bulk_update(
            video_objects, batch_size=200, fields=[f + "_quantile" for f in CRITERIAS]
        )

    @staticmethod
    def recompute_pareto():
        """Compute pareto-optimality."""
        # TODO: use a faster algorithm than O(|rated_videos|^2)

        logging.warning("Computing pareto-optimality...")
        video_objects = []
        for v in tqdm(Entity.objects.all()):
            new_pareto = v.get_pareto_optimal()
            if new_pareto != v.pareto_optimal:
                v.pareto_optimal = new_pareto
            video_objects.append(v)

        Entity.objects.bulk_update(
            video_objects, batch_size=200, fields=["pareto_optimal"]
        )

    def refresh_youtube_metadata(self, force=False):
        """
        Fetch and update video metadata from Youtube API.

        By default, the request will be executed only if the current metadata
        are older than `VIDEO_METADATA_EXPIRE_SECONDS`.
        The request can be forced with `force=True`.
        """
        from tournesol.utils.api_youtube import VideoNotFound, get_video_metadata

        if (
            not force
            and self.last_metadata_request_at is not None
            and (
                timezone.now() - self.last_metadata_request_at
                < timedelta(seconds=settings.VIDEO_METADATA_EXPIRE_SECONDS)
            )
        ):
            logging.debug(
                "Not refreshing metadata for video %s. Last attempt is too recent at %s",
                self.video_id,
                self.last_metadata_request_at,
            )
            return

        self.last_metadata_request_at = timezone.now()
        self.save(update_fields=["last_metadata_request_at"])
        try:
            metadata = get_video_metadata(self.video_id, compute_language=False)
        except VideoNotFound:
            metadata = {}

        if not metadata:
            return

        fields = [
            "name",
            "description",
            "publication_date",
            "uploader",
            "views",
            "duration",
            "metadata_timestamp",
        ]
        for f in fields:
            setattr(self, f, metadata[f])
        self.save(update_fields=fields)

    @classmethod
    def create_from_video_id(cls, video_id):
        from tournesol.utils.api_youtube import VideoNotFound, get_video_metadata
        try:
            extra_data = get_video_metadata(video_id)
        except VideoNotFound:
            raise
        tags = extra_data.pop('tags', [])
        video = cls.objects.create(video_id=video_id, **extra_data)
        for tag_name in tags:
            #  The return object is a tuple having first an instance of Tag, and secondly a bool
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            video.tags.add(tag)
        return video


class VideoCriteriaScore(models.Model):
    """Scores per criteria for Entities"""

    video = models.ForeignKey(
        to=Entity,
        on_delete=models.CASCADE,
        help_text="Foreign key to the video",
        related_name="criteria_scores",
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
    # quantiles are computed in the Entity.recompute_quantiles(),
    # called via the manage.py compute_quantile_pareto command
    # should be computed after every ml_train command (see the devops script)
    quantile = models.FloatField(
        default=1.0,
        null=False,
        blank=False,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Top quantile for all rated videos for aggregated scores"
        "for the given criteria. 0.0=best, 1.0=worst",
    )

    class Meta:
        unique_together = ["video", "criteria"]

    def __str__(self):
        return f"{self.video}/{self.criteria}/{self.score}"


class VideoRateLater(models.Model):
    """List of videos that a person wants to rate later."""

    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        help_text="Person who saves the video",
        related_name="videoratelaters",
    )
    video = models.ForeignKey(
        to=Entity,
        on_delete=models.CASCADE,
        help_text="Video in the rate later list",
        related_name="videoratelaters",
    )

    datetime_add = models.DateTimeField(
        auto_now_add=True,
        help_text="Time the video was added to the" " rate later list",
        null=True,
        blank=True,
    )

    class Meta:
        unique_together = ["user", "video"]
        ordering = ["user", "-datetime_add"]

    def __str__(self):
        return f"{self.user}/{self.video}@{self.datetime_add}"


class VideoRatingThankYou(models.Model):
    """Thank you for recommendations."""

    video = models.ForeignKey(
        Entity, on_delete=models.CASCADE, help_text="Video thanked for"
    )
    thanks_from = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="Who thanks for the video",
        related_name="thanks_from",
    )
    thanks_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="Who receives the thanks",
        related_name="thanks_to",
    )

    class Meta:
        unique_together = ["video", "thanks_from", "thanks_to"]

    def __str__(self):
        return "%s to %s for %s" % (self.thanks_from, self.thanks_to, self.video)


class VideoSelectorSkips(models.Model):
    """Count video being skipped in the Video Selector."""

    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name="skipped_videos",
        null=False,
        help_text="Person who skips the videos",
    )
    video = models.ForeignKey(
        to=Entity,
        on_delete=models.CASCADE,
        related_name="skips",
        null=False,
        help_text="Video being skipped",
    )
    datetime_add = models.DateTimeField(
        auto_now_add=True, help_text="Time the video was skipped", null=True, blank=True
    )

    def __str__(self):
        return f"{self.user}/{self.video}@{self.datetime_add}"
