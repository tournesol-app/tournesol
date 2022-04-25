from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .entity import Entity
from .poll import Poll


class EntityCriteriaScore(models.Model):
    """
    The score of an Entity for a given Criteria, in the scope of a given
    Poll.
    """

    entity = models.ForeignKey(
        to=Entity,
        on_delete=models.CASCADE,
        help_text="Foreign key to the video",
        related_name="criteria_scores",
    )
    poll = models.ForeignKey(
        Poll,
        on_delete=models.CASCADE,
        related_name="scores",
        default=Poll.default_poll_pk,
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
    deviation = models.FloatField(
        default=None,
        null=True,
        blank=True,
        help_text="A measure of deviation between the individual scores and the global 'score'. "
        "May also be understood as a measure of polarization",
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
        unique_together = ["entity", "poll", "criteria"]

    def __str__(self):
        return f"{self.entity}/{self.criteria}/{self.score}"
