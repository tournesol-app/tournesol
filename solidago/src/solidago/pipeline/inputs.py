import zipfile
from abc import ABC, abstractmethod
from functools import cached_property
from typing import BinaryIO, Optional, Union
from urllib.request import urlretrieve

import pandas as pd


class TournesolInput(ABC):
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

    @abstractmethod
    def get_individual_scores(
        self,
        criteria: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> Optional[pd.DataFrame]:
        raise NotImplementedError


class TournesolInputFromPublicDataset(TournesolInput):
    def __init__(self, dataset_zip: Union[str, BinaryIO]):
        if isinstance(dataset_zip, str) and (
            dataset_zip.startswith("http://") or dataset_zip.startswith("https://")
        ):
            dataset_zip, _headers = urlretrieve(dataset_zip)  # nosec B310

        with zipfile.ZipFile(dataset_zip) as zip_file:
            with (zipfile.Path(zip_file) / "comparisons.csv").open(mode="rb") as comparison_file:
                # keep_default_na=False is required otherwise some public usernames
                # such as "NA" are converted to float NaN.
                self.comparisons = pd.read_csv(comparison_file, keep_default_na=False)
                self.entity_id_to_video_id = pd.Series(
                    list(set(self.comparisons.video_a) | set(self.comparisons.video_b)),
                    name="video_id"
                )
                video_id_to_entity_id = {
                    video_id: entity_id
                    for (entity_id, video_id) in self.entity_id_to_video_id.items()
                }
                self.comparisons["entity_a"] = self.comparisons["video_a"].map(video_id_to_entity_id)
                self.comparisons["entity_b"] = self.comparisons["video_b"].map(video_id_to_entity_id)
                self.comparisons.drop(columns=["video_a", "video_b"], inplace=True)

            with (zipfile.Path(zip_file) / "users.csv").open(mode="rb") as users_file:
                # keep_default_na=False is required otherwise some public usernames
                # such as "NA" are converted to float NaN.
                self.users = pd.read_csv(users_file, keep_default_na=False)
                self.users.index.name = "user_id"

            username_to_user_id = pd.Series(
                data=self.users.index, index=self.users["public_username"]
            )
            self.comparisons = self.comparisons.join(username_to_user_id, on="public_username")

    @classmethod
    def download(cls) -> "TournesolInputFromPublicDataset":
        return cls(dataset_zip="https://api.tournesol.app/exports/all")

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

    def get_individual_scores(
        self,
        criteria: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> Optional[pd.DataFrame]:
        # TODO: read contributor scores from individual_scores.csv
        return None

    def get_user_index(self, public_username: str) -> Optional[int]:
        if self.users is None or "public_username" not in self.users:
            return None
        rows = self.users.loc[self.users["public_username"] == public_username]
        assert len(rows) <= 1
        if len(rows) == 0:
            return None
        return rows.index[0]
