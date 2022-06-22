"""
Models for Tournesol's main functions related to contributor's ratings
"""
from math import tau

from django.db import models
from django.db.models import Case, F, FilteredRelation, Func, Prefetch, Q, When
from django.db.models.functions import Coalesce

from core.models import User
from tournesol.utils.constants import MEHESTAN_MAX_SCALED_SCORE

from .entity import Entity
from .poll import ALGORITHM_MEHESTAN, Poll


class ContributorRatingQueryset(models.QuerySet):
    def with_scaled_scores(self):
        scaled_score_expression = Case(
            When(
                contributor_rating__poll__algorithm=ALGORITHM_MEHESTAN,
                then=(
                    4. * MEHESTAN_MAX_SCALED_SCORE / tau
                    * Func(
                        F("indiv_scaled_score") * F("contributor_rating__poll__scale"),
                        function="ATAN"
                    )
                )
            ),
            default=F("indiv_scaled_score")
        )
        scaled_uncertainty_expression = Case(
            When(
                contributor_rating__poll__algorithm=ALGORITHM_MEHESTAN,
                then=(
                    F("indiv_scaled_uncertainty")
                    * 4. * MEHESTAN_MAX_SCALED_SCORE / tau * F("contributor_rating__poll__scale")
                    / (1. + (F("contributor_rating__poll__scale") * F("indiv_scaled_score"))**2.)
                )
            ),
            default=F("indiv_scaled_uncertainty")
        )
        return self.prefetch_related(Prefetch(
            "criteria_scores",
            queryset=(
                ContributorRatingCriteriaScore
                .objects
                .alias(
                    scaling=FilteredRelation(
                        "contributor_rating__user__scalings",
                        condition=Q(
                            contributor_rating__user__scalings__poll=F("contributor_rating__poll"),
                            contributor_rating__user__scalings__user=F("contributor_rating__user"),
                            contributor_rating__user__scalings__criteria=F("criteria")
                        )
                    )
                )
                .alias(
                    scale=Coalesce(F("scaling__scale"), 1.0),
                    scale_uncertainty=Coalesce(F("scaling__scale"), 0.0),
                    translation=Coalesce(F("scaling__translation"), 0.0),
                    translation_uncertainty=Coalesce(F("scaling__translation_uncertainty"), 0.0),
                )
                .alias(
                    indiv_scaled_score=F("score") * F("scale") + F("translation"),
                    indiv_scaled_uncertainty=(
                        F("uncertainty") * F("scale")
                        + Func("score", function="ABS") * F("scale_uncertainty")
                        + F("translation_uncertainty")
                    )
                )
                .annotate(
                    scaled_score=scaled_score_expression,
                    scaled_uncertainty=scaled_uncertainty_expression,
                )
            ))
        )


class ContributorRating(models.Model):
    """Predictions by individual contributor models."""

    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        help_text="Entity being scored",
        related_name="contributorvideoratings",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="The contributor",
        related_name="contributorvideoratings",
    )
    poll = models.ForeignKey(
        Poll,
        on_delete=models.CASCADE,
        related_name="contributor_ratings"
    )
    is_public = models.BooleanField(
        default=False, null=False, help_text="Should the rating be public?"
    )

    class Meta:
        unique_together = ["user", "entity", "poll"]

    objects = ContributorRatingQueryset.as_manager()

    def __str__(self):
        return "%s on %s" % (self.user, self.entity)


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
        unique_together = ["contributor_rating", "criteria"]

    def __str__(self):
        return f"{self.contributor_rating}/{self.criteria}/{self.score}"
