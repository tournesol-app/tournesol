import zipfile
from abc import ABC, abstractmethod
from functools import cached_property
from typing import BinaryIO, Optional, Union
from urllib.request import urlretrieve

import pandas as pd
from django.db.models import Case, F, QuerySet, When
from django.db.models.expressions import RawSQL

from core.models import User
from tournesol.models import ComparisonCriteriaScore, ContributorRating, ContributorScaling, Entity


class MlInput(ABC):
    SCALING_CALIBRATION_MIN_ENTITIES_TO_COMPARE = 20
    SCALING_CALIBRATION_MIN_TRUST_SCORE = 0.1
    MAX_SCALING_CALIBRATION_USERS = 100

    @abstractmethod
    def get_comparisons(
        self,
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

    @property
    @abstractmethod
    def ratings_properties(self) -> pd.DataFrame:
        """Fetch data about contributor ratings properties

        Returns:
        - ratings_df: DataFrame with columns
            * `user_id`: int
            * `entity_id`: int or str
            * `is_public`: bool
            * `is_scaling_calibration_user`: bool
            * `trust_score`: float
        """
        raise NotImplementedError


class MlInputFromPublicDataset(MlInput):
    def __init__(self, dataset_zip: Union[str, BinaryIO]):
        if isinstance(dataset_zip, str) and (
            dataset_zip.startswith("http://") or dataset_zip.startswith("https://")
        ):
            dataset_zip, _headers = urlretrieve(dataset_zip)  # nosec B310

        with zipfile.ZipFile(dataset_zip) as zip_file:
            with (zipfile.Path(zip_file) / "comparisons.csv").open(mode="rb") as comparison_file:
                self.comparisons = pd.read_csv(comparison_file)
                self.comparisons.rename(
                    {"video_a": "entity_a", "video_b": "entity_b"}, axis=1, inplace=True
                )

            with (zipfile.Path(zip_file) / "users.csv").open(mode="rb") as users_file:
                self.users = pd.read_csv(users_file)
                self.users.index.name = "user_id"

            username_to_user_id = pd.Series(
                data=self.users.index, index=self.users["public_username"]
            )
            self.comparisons = self.comparisons.join(username_to_user_id, on="public_username")

    def get_comparisons(self, criteria=None, user_id=None) -> pd.DataFrame:
        dtf = self.comparisons.copy(deep=False)
        if criteria is not None:
            dtf = dtf[dtf.criteria == criteria]
        if user_id is not None:
            dtf = dtf[dtf.user_id == user_id]
        dtf["weight"] = 1
        return dtf[["user_id", "entity_a", "entity_b", "criteria", "score", "weight"]]

    @cached_property
    def ratings_properties(self):
        user_entities_pairs = pd.Series(
            iter(
                set(self.comparisons.groupby(["user_id", "entity_a"]).indices.keys())
                | set(self.comparisons.groupby(["user_id", "entity_b"]).indices.keys())
            )
        )
        dtf = pd.DataFrame([*user_entities_pairs], columns=["user_id", "entity_id"])
        dtf["is_public"] = True
        dtf["trust_score"] = dtf["user_id"].map(self.users["trust_score"])
        scaling_calibration_user_ids = (
            dtf[dtf.trust_score > self.SCALING_CALIBRATION_MIN_TRUST_SCORE]["user_id"]
            .value_counts(sort=True)[: self.MAX_SCALING_CALIBRATION_USERS]
            .index
        )
        dtf["is_scaling_calibration_user"] = dtf["user_id"].isin(scaling_calibration_user_ids)
        return dtf


class MlInputFromDb(MlInput):
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
            comparison__poll__name=self.poll_name
        )
        if criteria is not None:
            scores_queryset = scores_queryset.filter(criteria=criteria)

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
            return dtf[["user_id", "entity_a", "entity_b", "criteria", "score", "weight"]]

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

    @cached_property
    def ratings_properties(self):
        values = (
            ContributorRating.objects.filter(
                poll__name=self.poll_name,
            )
            .annotate(
                is_scaling_calibration_user=Case(
                    When(user__in=self.get_scaling_calibration_users().values("id"), then=True),
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
