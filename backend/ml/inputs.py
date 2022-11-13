from abc import ABC, abstractmethod
from typing import Optional

import pandas as pd
from django.db.models import Case, F, QuerySet, When
from django.db.models.expressions import RawSQL

from core.models import User
from tournesol.models import ComparisonCriteriaScore, ContributorRating, ContributorScaling, Entity


class MlInput(ABC):
    @abstractmethod
    def get_comparisons(
        self,
        trusted_only=False,
        criteria: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> pd.DataFrame:
        """Fetch data about comparisons submitted by users

        Returns:
        - comparisons_df: DataFrame with columns
            * `user_id`: int
            * `entity_a`: int or str
            * `entity_b`: int or str
            * `criteria`: str
            * `score`: float
            * `weight`: float
        """
        raise NotImplementedError

    @abstractmethod
    def get_ratings_properties(self) -> pd.DataFrame:
        """Fetch data about contributor ratings properties

        Returns:
        - ratings_df: DataFrame with columns
            * `user_id`: int
            * `entity_id`: int or str
            * `is_public`: bool
            * `is_trusted`: bool
            * `is_supertrusted`: bool
        """
        raise NotImplementedError


class MlInputFromPublicDataset(MlInput):
    def __init__(self, csv_file):
        self.public_dataset = pd.read_csv(csv_file)
        self.public_dataset.rename(
            {"video_a": "entity_a", "video_b": "entity_b"}, axis=1, inplace=True
        )
        self.public_dataset["user_id"], self.user_indices = self.public_dataset[
            "public_username"
        ].factorize()

    def get_comparisons(
        self, trusted_only=False, criteria=None, user_id=None
    ) -> pd.DataFrame:
        dtf = self.public_dataset.copy(deep=False)
        if criteria is not None:
            dtf = dtf[dtf.criteria == criteria]
        if user_id is not None:
            dtf = dtf[dtf.user_id == user_id]
        return dtf[["user_id", "entity_a", "entity_b", "criteria", "score", "weight"]]

    def get_ratings_properties(self):
        # TODO support trust_scores from the public dataset
        user_entities_pairs = pd.Series(
            iter(
                set(self.public_dataset.groupby(["user_id", "entity_a"]).indices.keys())
                | set(
                    self.public_dataset.groupby(["user_id", "entity_b"]).indices.keys()
                )
            )
        )
        dtf = pd.DataFrame([*user_entities_pairs], columns=["user_id", "entity_id"])
        dtf["is_public"] = True
        top_users = dtf.value_counts("user_id").index[:6]
        dtf["is_trusted"] = dtf["is_supertrusted"] = dtf["user_id"].isin(top_users)
        return dtf


class MlInputFromDb(MlInput):
    SUPERTRUSTED_MIN_ENTITIES_TO_COMPARE = 20
    MAX_SUPERTRUSTED_USERS = 100

    def __init__(self, poll_name: str):
        self.poll_name = poll_name

    def get_supertrusted_users(self) -> QuerySet[User]:
        n_alternatives = (
            Entity.objects.filter(comparisons_entity_1__poll__name=self.poll_name)
            .union(
                Entity.objects.filter(comparisons_entity_2__poll__name=self.poll_name)
            )
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
        if n_alternatives <= self.SUPERTRUSTED_MIN_ENTITIES_TO_COMPARE:
            # The number of alternatives is low enough to consider as supertrusted
            # all trusted users who have compared all alternatives.
            have_compared_all_alternatives = users.filter(
                n_compared_entities__gte=n_alternatives
            )
            return User.with_trusted_email().filter(pk__in=have_compared_all_alternatives)

        n_supertrusted_seed = User.supertrusted_seed_users().count()
        return User.supertrusted_seed_users().union(
            users.filter(
                pk__in=User.with_trusted_email(),
                n_compared_entities__gte=self.SUPERTRUSTED_MIN_ENTITIES_TO_COMPARE,
            )
            .exclude(pk__in=User.supertrusted_seed_users())
            .order_by("-n_compared_entities")[
                : self.MAX_SUPERTRUSTED_USERS - n_supertrusted_seed
            ]
        )

    def get_comparisons(
        self, trusted_only=False, criteria=None, user_id=None
    ) -> pd.DataFrame:
        scores_queryset = ComparisonCriteriaScore.objects.filter(
            comparison__poll__name=self.poll_name
        )
        if criteria is not None:
            scores_queryset = scores_queryset.filter(criteria=criteria)

        if trusted_only:
            scores_queryset = scores_queryset.filter(
                comparison__user__in=User.with_trusted_email()
            )

        if user_id is not None:
            scores_queryset = scores_queryset.filter(comparison__user_id=user_id)

        values = scores_queryset.values(
            "score",
            "criteria",
            "weight",
            entity_a=F("comparison__entity_1_id"),
            entity_b=F("comparison__entity_2_id"),
            user_id=F("comparison__user_id"),
        )
        if len(values) > 0:
            dtf = pd.DataFrame(values)
            return dtf[
                ["user_id", "entity_a", "entity_b", "criteria", "score", "weight"]
            ]

        return pd.DataFrame(
            columns=[
                "user_id",
                "entity_a",
                "entity_b",
                "criteria",
                "score",
                "weight",
            ]
        )

    def get_ratings_properties(self):
        # TODO should this be cached?
        values = (
            ContributorRating.objects.filter(
                poll__name=self.poll_name,
            )
            .annotate(
                is_trusted=Case(
                    When(user__in=User.with_trusted_email(), then=True), default=False
                ),
                is_supertrusted=Case(
                    When(user__in=self.get_supertrusted_users().values("id"), then=True),
                    default=False,
                ),
            )
            .values(
                "user_id",
                "entity_id",
                "is_public",
                "is_trusted",
                "is_supertrusted",
                trust_score=F("user__trust_score"),
            )
        )
        if len(values) == 0:
            return pd.DataFrame(
                columns=[
                    "user_id",
                    "entity_id",
                    "is_public",
                    "is_trusted",
                    "is_supertrusted",
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
            "translation_uncertainty"
        )
        if len(values) == 0:
            return pd.DataFrame(
                columns=[
                    "user_id",
                    "criteria",
                    "scale",
                    "scale_uncertainty",
                    "translation",
                    "translation_uncertainty"
                ]
            )
        return pd.DataFrame(values)
