import zipfile
from abc import ABC, abstractmethod
from functools import cached_property
from typing import BinaryIO, Optional, Union
from urllib.request import urlretrieve

import pandas as pd

from solidago.privacy_settings import PrivacySettings
from solidago.judgments import DataFrameJudgments
from solidago.scoring_model import DirectScoringModel


class PipelineInput(ABC):
    """
    An abstract base class for handling input data of Solidago pipeline.

    This class provides an interface for retrieving and processing comparison data,
    user ratings, individual scores, and vouches.

    Notes
    -----
    This is an abstract base class that must be subclassed and have its abstract
    methods implemented to provide concrete data retrieval functionality.
    """

    SCALING_CALIBRATION_MIN_TRUST_SCORE = 0.1
    MAX_SCALING_CALIBRATION_USERS = 100

    @abstractmethod
    def get_comparisons(
        self,
        criterion: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> pd.DataFrame:
        """Fetch data about comparisons submitted by users

        Returns:
        - comparisons_df: DataFrame with columns
            * `user_id`: int
            * `entity_a`: int or str
            * `entity_b`: int or str
            * `criterion`: str
            * `score`: float
            * `score_max`: int
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
        """
        raise NotImplementedError

    @abstractmethod
    def get_individual_scores(
        self,
        user_id: Optional[int] = None,
        criterion: Optional[str] = None,
    ) -> pd.DataFrame:
        """Fetch data about previously computed individual scores

        Returns:
        - DataFrame with columns
            * `user_id`: int
            * `entity_id`: int
            * `criterion`: str
            * `score`: float
            * `raw_score`: float (optional column, used to initialize preference learning)
        """
        raise NotImplementedError

    @abstractmethod
    def get_vouches(self):
        """Fetch data about vouches shared between users

        Returns:
        - DataFrame with columns
            * `voucher`: int, user_id of the user who gives the vouch
            * `vouchee`: int, user_id of the user who receives the vouch
            * `vouch`: float, value of this vouch
        """
        raise NotImplementedError

    def get_users(self):
        """
        Returns:
        - DataFrame with columns
            * `user_id`: int (index)
            * `trust_score`: float
            * `is_pretrusted`: boolean
        """
        raise NotImplementedError

    def get_pipeline_kwargs(self, criterion: str):
        ratings_properties = self.ratings_properties
        users = self.get_users()
        vouches = self.get_vouches()
        comparisons = self.get_comparisons(criterion=criterion)
        entities_ids = set(comparisons["entity_a"].unique()) | set(
            comparisons["entity_b"].unique()
        )
        entities = pd.DataFrame(index=list(entities_ids))

        privacy = PrivacySettings()
        for rating in ratings_properties.itertuples():
            privacy[(rating.user_id, rating.entity_id)] = not rating.is_public

        judgments = DataFrameJudgments(
            comparisons=comparisons.rename(
                columns={
                    "score": "comparison",
                    "score_max": "comparison_max",
                }
            )
        )

        individual_scores = self.get_individual_scores(criterion=criterion)
        if "raw_score" in individual_scores:
            init_user_models = {
                user_id: DirectScoringModel(
                    {row.entity_id: (row.raw_score, 0.0, 0.0) for row in user_df.itertuples()}
                )
                for (user_id, user_df) in individual_scores.groupby("user_id")
            }
        else:
            init_user_models = None

        return {
            "users": users,
            "vouches": vouches,
            "entities": entities,
            "privacy": privacy,
            "judgments": judgments,
            "init_user_models": init_user_models,
        }

    def get_comparisons_counts(
        self, criterion: Optional[str] = None, user_id: Optional[int] = None
    ):
        comparisons = self.get_comparisons(criterion=criterion, user_id=user_id)
        return (
            pd.concat(
                [
                    comparisons[["user_id", "entity_a", "criterion"]].rename(
                        columns={"entity_a": "entity_id"}
                    ),
                    comparisons[["user_id", "entity_b", "criterion"]].rename(
                        columns={"entity_b": "entity_id"}
                    ),
                ]
            )
            .groupby(["user_id", "entity_id", "criterion"])
            .size()
            .reset_index(name="n_comparisons")
        )


class TournesolDataset(PipelineInput):
    def __init__(self, dataset_zip: Union[str, BinaryIO]):
        if isinstance(dataset_zip, str) and (
            dataset_zip.startswith("http://") or dataset_zip.startswith("https://")
        ):
            dataset_zip, _headers = urlretrieve(dataset_zip)  # nosec B310

        with zipfile.ZipFile(dataset_zip) as zip_file:
            with (zipfile.Path(zip_file) / "users.csv").open(mode="rb") as users_file:
                # keep_default_na=False is required otherwise some public usernames
                # such as "NA" are converted to float NaN.
                self.users = pd.read_csv(users_file, keep_default_na=False)
                self.users.index.name = "user_id"
                # Fill trust_score on newly created users for which it was not computed yet
                self.users.trust_score = pd.to_numeric(self.users.trust_score).fillna(0.0)

            with (zipfile.Path(zip_file) / "collective_criteria_scores.csv").open(
                mode="rb"
            ) as collective_scores_file:
                # keep_default_na=False is required otherwise some public usernames
                # such as "NA" are converted to float NaN.
                collective_scores = pd.read_csv(
                    collective_scores_file, keep_default_na=False
                ).rename(columns={"criteria": "criterion"})

            with (zipfile.Path(zip_file) / "comparisons.csv").open(mode="rb") as comparison_file:
                # keep_default_na=False is required otherwise some public usernames
                # such as "NA" are converted to float NaN.
                comparisons = pd.read_csv(comparison_file, keep_default_na=False).rename(
                    columns={"criteria": "criterion"}
                )

            with (zipfile.Path(zip_file) / "vouchers.csv").open(mode="rb") as vouchers_file:
                # keep_default_na=False is required otherwise some public usernames
                # such as "NA" are converted to float NaN.
                self.vouchers = pd.read_csv(vouchers_file, keep_default_na=False)

            self.username_to_user_id = pd.Series(
                data=self.users.index,
                index=self.users["public_username"],
            )

            self.entity_id_to_video_id = pd.Series(
                sorted(
                    set(comparisons.video_a)
                    | set(comparisons.video_b)
                    | set(collective_scores.video)
                ),
                name="video_id",
            )

            self.video_id_to_entity_id = {
                video_id: entity_id for (entity_id, video_id) in self.entity_id_to_video_id.items()
            }

            # Convert video ids (str) to entity ids (int)
            self.collective_scores = collective_scores.assign(
                entity_id=collective_scores["video"].map(self.video_id_to_entity_id)
            ).drop(columns=["video"])

            self.comparisons = comparisons.assign(
                entity_a=comparisons["video_a"].map(self.video_id_to_entity_id),
                entity_b=comparisons["video_b"].map(self.video_id_to_entity_id),
                user_id=comparisons["public_username"].map(self.username_to_user_id),
            ).drop(columns=["video_a", "video_b"])

            with (zipfile.Path(zip_file) / "individual_criteria_scores.csv").open(
                mode="rb"
            ) as individual_scores_file:
                # keep_default_na=False is required otherwise some public usernames
                # such as "NA" are converted to float NaN.
                individual_scores = pd.read_csv(individual_scores_file, keep_default_na=False)
                # Convert usernames and video_id to user_id and entity_id
                self.individual_scores = (
                    individual_scores.assign(
                        entity_id=individual_scores["video"].map(self.video_id_to_entity_id),
                        user_id=individual_scores["public_username"].map(self.username_to_user_id),
                    )
                    .rename(columns={"criteria": "criterion"})
                    .drop(columns=["public_username", "video"])
                )

    @classmethod
    def download(cls) -> "TournesolDataset":
        return cls(dataset_zip="https://api.tournesol.app/exports/all")

    def get_comparisons(self, criterion=None, user_id=None) -> pd.DataFrame:
        dtf = self.comparisons.copy(deep=False)
        if criterion is not None:
            dtf = dtf[dtf.criterion == criterion]
        if user_id is not None:
            dtf = dtf[dtf.user_id == user_id]
        dtf["weight"] = 1
        if "score_max" not in dtf:
            # For compatibility with older datasets
            dtf["score_max"] = 10
        return dtf[
            [
                "user_id",
                "entity_a",
                "entity_b",
                "criterion",
                "score",
                "score_max",
                "weight",
            ]
        ]

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
        return dtf

    def get_individual_scores(
        self,
        user_id: Optional[int] = None,
        criterion: Optional[str] = None,
        with_n_comparisons=False,
    ) -> pd.DataFrame:
        dtf = self.individual_scores
        if criterion is not None:
            dtf = dtf[dtf.criterion == criterion]
        if user_id is not None:
            dtf = dtf[dtf.user_id == user_id]

        dtf = dtf[
            [
                "user_id",
                "entity_id",
                "criterion",
                "score",
                "uncertainty",
                "voting_right",
            ]
        ]

        if with_n_comparisons:
            comparison_counts = self.get_comparisons_counts(user_id=user_id, criterion=criterion)
            dtf = dtf.merge(
                comparison_counts, how="left", on=["user_id", "entity_id", "criterion"]
            )

        return dtf

    def get_collective_scores(
        self,
        entity_id: Optional[str] = None,
        criterion: Optional[str] = None,
    ) -> pd.DataFrame:
        dtf: pd.DataFrame = self.collective_scores
        if criterion is not None:
            dtf = dtf[dtf["criterion"] == criterion]
        if entity_id is not None:
            dtf = dtf[dtf["entity_id"] == entity_id]

        counts = (
            self.get_comparisons_counts(criterion=criterion)
            .groupby(["criterion", "entity_id"])
            .agg(
                n_comparisons=("n_comparisons", "sum"),
                n_users=("user_id", "nunique"),
            )
        )

        return (
            dtf.join(counts, how="left", on=["criterion", "entity_id"])
            # Entities that have been compared privately only
            # will not appear in comparisons.csv. That's why we need
            # to fill for missing values here.
            .fillna({"n_comparisons": 0, "n_users": 0}).astype(
                {"n_comparisons": "int64", "n_users": "int64"}
            )
        )

    def get_vouches(self):
        vouchers = self.vouchers[
            self.vouchers.by_username.isin(self.username_to_user_id.index)
            & self.vouchers.to_username.isin(self.username_to_user_id.index)
        ]
        return pd.DataFrame(
            {
                "voucher": vouchers.by_username.map(self.username_to_user_id),
                "vouchee": vouchers.to_username.map(self.username_to_user_id),
                "vouch": vouchers.value,
            }
        )

    def get_users(self):
        users_df = pd.DataFrame(
            {
                "trust_score": self.users["trust_score"],
            },
            index=self.users.index,
        )
        # TODO: export pretrusted status in public dataset
        users_df["is_pretrusted"] = users_df["trust_score"] >= 0.8
        return users_df
