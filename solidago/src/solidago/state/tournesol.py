import zipfile
from functools import cached_property
from typing import BinaryIO, Optional, Union
from urllib.request import urlretrieve

import pandas as pd

from .base import *


class TournesolExport(State):
    def __init__(self, dataset_zip: Union[str, BinaryIO]="https://api.tournesol.app/exports/all"):
        if isinstance(dataset_zip, str) and (
            dataset_zip.startswith("http://") or dataset_zip.startswith("https://")
        ):
            dataset_zip, _headers = urlretrieve(dataset_zip)  # nosec B310

        def load(filename, columns=dict()):
            with zipfile.ZipFile(dataset_zip) as zip_file:
                with (zipfile.Path(zip_file) / f"{filename}.csv").open(mode="rb") as f:
                    # keep_default_na=False is required otherwise some public usernames
                    # such as "NA" are converted to float NaN.
                    return pd.read_csv(f, keep_default_na=False).rename(columns)
            
        users = User(load("users", { "public_username", "username" }))
        vouches = Vouches(load("vouchers", { "by_username": "by", "to_username": "to", "value": "weight" }))
        judgments = Judgments(
            comparisons=Comparisons(load("comparisons", { 
                "public_username": "username",
                "video_a": "left_id",
                "video_b": "right_id",
                "criteria": "criterion",
                "score": "comparison",
                "score_max": "comparison_max"
            }))
        )
        
        pd_global_scores = load("collective_criteria_scores", { 
            "criteria": "criterion", 
            "video": "entity_id",
        })
        pd_user_scores = load("comparisons", { 
            "criteria": "criterion", 
            "video": "entity_id",
            "public_username": "username"
        })
        
        entities = Entities({ "entity_id": list(set(pd_global_scores["entity_id"])) })
        
        privacy = Privacy()
        for _, r in pd_user_scores:
            privacy[users.get(r["username"])]
        
        voting_rights = VotingRights()
        
        user_models = ScoringModelDict(),
        global_model: ScoringModel = DirectScoring(),
        
        privacy = Privacy() # TODO
        voting_rights = VotingRights()
        super().__init__(users, vouches, entities, privacy, judgments, voting_rights, user_models, global_model)

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
