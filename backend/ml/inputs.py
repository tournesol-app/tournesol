from abc import ABC, abstractmethod

import pandas as pd
from django.db.models import Case, F, When

from core.models import User
from tournesol.models import ComparisonCriteriaScore
from tournesol.models.ratings import ContributorRating


class MlInput(ABC):
    @abstractmethod
    def get_comparisons(self, trusted_only=False, criteria=None) -> pd.DataFrame:
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
        pass

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
        pass


class MlInputFromPublicDataset(MlInput):
    def __init__(self, csv_file):
        self.public_dataset = pd.read_csv(csv_file)
        self.public_dataset.rename(
            {"video_a": "entity_a", "video_b": "entity_b"}, axis=1, inplace=True
        )
        self.public_dataset["user_id"], self.user_indices = self.public_dataset[
            "public_username"
        ].factorize()

    def get_comparisons(self, trusted_only=False, criteria=None) -> pd.DataFrame:
        df = self.public_dataset.copy(deep=False)
        if criteria is not None:
            df = df[df.criteria == criteria]
        return df[["user_id", "entity_a", "entity_b", "criteria", "score", "weight"]]

    def get_ratings_properties(self):
        user_entities_pairs = pd.Series(
            iter(
                set(self.public_dataset.groupby(["user_id", "entity_a"]).indices.keys())
                | set(
                    self.public_dataset.groupby(["user_id", "entity_b"]).indices.keys()
                )
            )
        )
        df = pd.DataFrame([*user_entities_pairs], columns=["user_id", "entity_id"])
        df["is_public"] = True
        top_users = df.value_counts("user_id").index[:6]
        df["is_trusted"] = df["is_supertrusted"] = df["user_id"].isin(top_users)
        return df


class MlInputFromDb(MlInput):
    def __init__(self, poll_name):
        self.poll_name = poll_name

    def get_comparisons(self, trusted_only=False, criteria=None) -> pd.DataFrame:
        scores_queryset = ComparisonCriteriaScore.objects.filter(
            comparison__poll__name=self.poll_name
        )
        if criteria is not None:
            scores_queryset = scores_queryset.filter(criteria=criteria)

        if trusted_only:
            scores_queryset = scores_queryset.filter(
                comparison__user__in=User.trusted_users()
            )

        values = scores_queryset.values(
            "score",
            "criteria",
            "weight",
            entity_a=F("comparison__entity_1_id"),
            entity_b=F("comparison__entity_2_id"),
            user_id=F("comparison__user_id"),
        )
        if len(values) > 0:
            df = pd.DataFrame(values)
            return df[
                ["user_id", "entity_a", "entity_b", "criteria", "score", "weight"]
            ]
        else:
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
        values = (
            ContributorRating.objects.filter(
                poll__name=self.poll_name,
            )
            .annotate(
                is_trusted=Case(
                    When(user__in=User.trusted_users(), then=True), default=False
                ),
                is_supertrusted=Case(
                    When(user__in=User.supertrusted_users(), then=True), default=False
                ),
            )
            .values(
                "user_id",
                "entity_id",
                "is_public",
                "is_trusted",
                "is_supertrusted",
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
                ]
            )
        return pd.DataFrame(values)
