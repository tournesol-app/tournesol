"""
Models for Tournesol's main functions related to contributor's ratings
"""

from django.db import models
from django.db.models import Count, F, FilteredRelation, Max, OuterRef, Q, Subquery

from core.models import User

from .entity import Entity
from .poll import Poll


class ContributorRatingQueryset(models.QuerySet):
    _related_comparisons_is_annotated = False

    def _annotate_related_comparisons(self):
        if self._related_comparisons_is_annotated:
            return self
        self._related_comparisons_is_annotated = True
        return self.annotate(
            related_comparisons=FilteredRelation(
                "user__comparisons",
                condition=(
                    Q(user__comparisons__poll=F("poll"))
                    & (
                        Q(user__comparisons__entity_1=F("entity"))
                        | Q(user__comparisons__entity_2=F("entity"))
                    )
                ),
            )
        )

    def annotate_n_comparisons(self):
        return (
            self
            ._annotate_related_comparisons()
            .annotate(n_comparisons=Count("related_comparisons"))
        )

    def annotate_last_compared_at(self):
        return (
            self
            ._annotate_related_comparisons()
            .annotate(last_compared_at=Max("related_comparisons__datetime_lastedit"))
        )

    def annotate_collective_score(self):
        # pylint: disable=import-outside-toplevel
        from .entity_poll_rating import EntityPollRating
        collective_score = (
            EntityPollRating.objects.filter(poll=OuterRef("poll"), entity=OuterRef("entity"))
            .values("tournesol_score")
        )
        return self.annotate(collective_score=Subquery(collective_score))

    def annotate_individual_score(self, poll: Poll):
        individual_score = (
            ContributorRatingCriteriaScore.objects
            .filter(contributor_rating=OuterRef("pk"), criteria=poll.main_criteria)
            .values("score")
        )
        return self.annotate(individual_score=Subquery(individual_score))


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
        Poll, on_delete=models.CASCADE, related_name="contributor_ratings"
    )
    is_public = models.BooleanField(
        default=False, null=False, help_text="Should the rating be public?"
    )

    class Meta:
        unique_together = ["user", "entity", "poll"]

    objects = ContributorRatingQueryset.as_manager()

    def __str__(self):
        return f"{self.user} on {self.entity}"


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
        db_index=True,
        help_text="Name of the criteria",
    )
    score = models.FloatField(
        default=0,
        blank=False,
        help_text="Score for the given criteria, after individual and poll scalings applied",
    )
    uncertainty = models.FloatField(
        default=0,
        blank=False,
        help_text="Uncertainty about the criteria score",
    )
    raw_score = models.FloatField(
        default=0,
        help_text="Computed individual score without any scaling applied",
    )
    raw_uncertainty = models.FloatField(
        default=0,
        help_text="Computed individual uncertainty without any scaling applied",
    )
    voting_right = models.FloatField(
        default=0,
        help_text="Voting right computed based on trust scores and contributors having rated the "
        "entity on the criteria",
    )

    class Meta:
        unique_together = ["contributor_rating", "criteria"]

    def __str__(self):
        return f"{self.contributor_rating}/{self.criteria}/{self.score}"
