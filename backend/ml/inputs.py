from functools import cached_property
from typing import Optional

import pandas as pd
from django.db.models import Case, F, QuerySet, When
from django.db.models.expressions import RawSQL
from solidago.pipeline import TournesolInput

from core.models import User
from tournesol.models import (
    ComparisonCriteriaScore,
    ContributorRating,
    ContributorRatingCriteriaScore,
    ContributorScaling,
    Entity,
)


class MlInputFromDb(TournesolInput):
    SCALING_CALIBRATION_MIN_ENTITIES_TO_COMPARE = 20

    def __init__(self, poll_name: str):
        self.poll_name = poll_name

    def get_scaling_calibration_users(self) -> QuerySet[User]:
        n_alternatives = (
            Entity.objects.filter(comparisons_entity_1__poll__name=self.poll_name)
            .union(Entity.objects.filter(comparisons_entity_2__poll__name=self.poll_name))
            .count()
        )
        users = User.objects.alias(
            n_compared_entities=RawSQL(
                """
                SELECT COUNT(DISTINCT e.id)
                FROM tournesol_entity e
                INNER JOIN tournesol_comparison c
                    ON (c.entity_1_id = e.id OR c.entity_2_id = e.id)
                INNER JOIN tournesol_poll p
                    ON (p.id = c.poll_id AND p.name = %s)
                WHERE c.user_id = "core_user"."id"
                """,
                (self.poll_name,),
            )
        )
        if n_alternatives <= self.SCALING_CALIBRATION_MIN_ENTITIES_TO_COMPARE:
            # The number of alternatives is low enough to consider as calibration users
            # all trusted users who have compared all alternatives.
            return users.filter(
                is_active=True,
                trust_score__gt=self.SCALING_CALIBRATION_MIN_TRUST_SCORE,
                n_compared_entities__gte=n_alternatives,
            )

        return users.filter(
            is_active=True,
            trust_score__gt=self.SCALING_CALIBRATION_MIN_TRUST_SCORE,
            n_compared_entities__gte=self.SCALING_CALIBRATION_MIN_ENTITIES_TO_COMPARE,
        ).order_by("-n_compared_entities")[: self.MAX_SCALING_CALIBRATION_USERS]

    def get_comparisons(self, criteria=None, user_id=None) -> pd.DataFrame:
        scores_queryset = ComparisonCriteriaScore.objects.filter(
            comparison__poll__name=self.poll_name,
            comparison__user__is_active=True,
        )
        if criteria is not None:
            scores_queryset = scores_queryset.filter(criteria=criteria)

        if user_id is not None:
            scores_queryset = scores_queryset.filter(comparison__user_id=user_id)

        values = scores_queryset.values(
            "score",
            "score_max",
            "criteria",
            "weight",
            entity_a=F("comparison__entity_1_id"),
            entity_b=F("comparison__entity_2_id"),
            user_id=F("comparison__user_id"),
        )
        if len(values) > 0:
            dtf = pd.DataFrame(values)
            return dtf[
                ["user_id", "entity_a", "entity_b", "criteria", "score", "score_max", "weight"]
            ]

        return pd.DataFrame(
            columns=[
                "user_id",
                "entity_a",
                "entity_b",
                "criteria",
                "score",
                "score_max",
                "weight",
            ]
        )

    @cached_property
    def ratings_properties(self):
        # This makes sure that `get_scaling_calibration_users()` is evaluated separately, as the
        # table names mentionned in its RawSQL query could conflict with the current queryset.
        scaling_calibration_user_ids = list(self.get_scaling_calibration_users().values_list("id"))
        values = (
            ContributorRating.objects.filter(
                poll__name=self.poll_name,
            )
            .annotate(
                is_scaling_calibration_user=Case(
                    When(user__in=scaling_calibration_user_ids, then=True),
                    default=False,
                ),
            )
            .values(
                "user_id",
                "entity_id",
                "is_public",
                "is_scaling_calibration_user",
                trust_score=F("user__trust_score"),
            )
        )
        if len(values) == 0:
            return pd.DataFrame(
                columns=[
                    "user_id",
                    "entity_id",
                    "is_public",
                    "is_scaling_calibration_user",
                    "trust_score",
                ]
            )
        return pd.DataFrame(values)

    def get_user_scalings(self, user_id=None) -> pd.DataFrame:
        """Fetch saved invidiual scalings
        Returns:
        - ratings_df: DataFrame with columns
            * `user_id`: int
            * `criteria`: str
            * `scale`: float
            * `scale_uncertainty`: float
            * `translation`: float
            * `translation_uncertainty`: float
        """

        scalings = ContributorScaling.objects.filter(poll__name=self.poll_name)
        if user_id is not None:
            scalings = scalings.filter(user_id=user_id)
        values = scalings.values(
            "user_id",
            "criteria",
            "scale",
            "scale_uncertainty",
            "translation",
            "translation_uncertainty",
        )
        if len(values) == 0:
            return pd.DataFrame(
                columns=[
                    "user_id",
                    "criteria",
                    "scale",
                    "scale_uncertainty",
                    "translation",
                    "translation_uncertainty",
                ]
            )
        return pd.DataFrame(values)

    def get_individual_scores(
        self, criteria: Optional[str] = None, user_id: Optional[int] = None
    ) -> pd.DataFrame:
        scores_queryset = ContributorRatingCriteriaScore.objects.filter(
            contributor_rating__poll__name=self.poll_name,
            contributor_rating__user__is_active=True,
        )
        if criteria is not None:
            scores_queryset = scores_queryset.filter(criteria=criteria)
        if user_id is not None:
            scores_queryset = scores_queryset.filter(contributor_rating__user_id=user_id)

        values = scores_queryset.values(
            "raw_score",
            "criteria",
            entity=F("contributor_rating__entity_id"),
            user_id=F("contributor_rating__user_id"),
        )
        if len(values) == 0:
            return pd.DataFrame(columns=["user_id", "entity", "criteria", "raw_score"])

        dtf = pd.DataFrame(values)
        return dtf[["user_id", "entity", "criteria", "raw_score"]]
