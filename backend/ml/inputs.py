from functools import cached_property
from typing import Optional

import pandas as pd
from django.db.models import F, Q
from solidago.pipeline import PipelineInput

from core.models import User
from tournesol.models import (
    ComparisonCriteriaScore,
    ContributorRating,
    ContributorRatingCriteriaScore,
    ContributorScaling,
)
from vouch.models import Voucher


class MlInputFromDb(PipelineInput):
    def __init__(self, poll_name: str):
        self.poll_name = poll_name

    def get_comparisons(self, criterion=None, user_id=None) -> pd.DataFrame:
        scores_queryset = ComparisonCriteriaScore.objects.filter(
            comparison__poll__name=self.poll_name,
            comparison__user__is_active=True,
        )
        if criterion is not None:
            scores_queryset = scores_queryset.filter(criteria=criterion)

        if user_id is not None:
            scores_queryset = scores_queryset.filter(comparison__user_id=user_id)

        values = scores_queryset.values(
            "score",
            "score_max",
            "weight",
            criterion=F("criteria"),
            entity_a=F("comparison__entity_1_id"),
            entity_b=F("comparison__entity_2_id"),
            user_id=F("comparison__user_id"),
        )
        if len(values) > 0:
            dtf = pd.DataFrame(values)
            return dtf[
                ["user_id", "entity_a", "entity_b", "criterion", "score", "score_max", "weight"]
            ]

        return pd.DataFrame(
            columns=[
                "user_id",
                "entity_a",
                "entity_b",
                "criterion",
                "score",
                "score_max",
                "weight",
            ]
        )

    @cached_property
    def ratings_properties(self):
        # This makes sure that `get_scaling_calibration_users()` is evaluated separately, as the
        # table names mentionned in its RawSQL query could conflict with the current queryset.
        values = ContributorRating.objects.filter(
            poll__name=self.poll_name,
        ).values(
            "user_id",
            "entity_id",
            "is_public",
        )
        if len(values) == 0:
            return pd.DataFrame(
                columns=[
                    "user_id",
                    "entity_id",
                    "is_public",
                ]
            )
        return pd.DataFrame(values)

    def get_user_scalings(self, user_id=None) -> pd.DataFrame:
        """Fetch saved invidiual scalings
        Returns:
        - ratings_df: DataFrame with columns
            * `user_id`: int
            * `criterion`: str
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
            "scale",
            "scale_uncertainty",
            "translation",
            "translation_uncertainty",
            criterion=F("criteria"),

        )
        if len(values) == 0:
            return pd.DataFrame(
                columns=[
                    "user_id",
                    "criterion",
                    "scale",
                    "scale_uncertainty",
                    "translation",
                    "translation_uncertainty",
                ]
            )
        return pd.DataFrame(values)

    def get_individual_scores(
        self, user_id: Optional[int] = None, criterion: Optional[str] = None,
    ) -> pd.DataFrame:
        scores_queryset = ContributorRatingCriteriaScore.objects.filter(
            contributor_rating__poll__name=self.poll_name,
            contributor_rating__user__is_active=True,
        )
        if criterion is not None:
            scores_queryset = scores_queryset.filter(criteria=criterion)
        if user_id is not None:
            scores_queryset = scores_queryset.filter(contributor_rating__user_id=user_id)

        values = scores_queryset.values(
            "raw_score",
            criterion=F("criteria"),
            entity_id=F("contributor_rating__entity_id"),
            user_id=F("contributor_rating__user_id"),
        )
        if len(values) == 0:
            return pd.DataFrame(columns=["user_id", "entity_id", "criterion", "raw_score"])

        dtf = pd.DataFrame(values)
        return dtf[["user_id", "entity_id", "criterion", "raw_score"]]

    def get_vouches(self):
        values = Voucher.objects.filter(
            by__is_active=True,
            to__is_active=True,
        ).values(
            voucher=F("by__id"),
            vouchee=F("to__id"),
            vouch=F("value"),
        )
        return pd.DataFrame(values, columns=["voucher", "vouchee", "vouch"])

    def get_users(self):
        values = (
            User.objects
            .filter(is_active=True)
            .annotate(is_pretrusted=Q(pk__in=User.with_trusted_email()))
            .values(
                "is_pretrusted",
                "trust_score",
                user_id=F("id"),
            )
        )
        return pd.DataFrame(
            data=values,
            columns=["user_id", "is_pretrusted", "trust_score"],
        ).set_index("user_id")
