import zipfile
from functools import cached_property
from typing import BinaryIO, Optional, Union
from urllib.request import urlretrieve
from pandas import DataFrame, Series

import pandas as pd

from .base import *


class TournesolExport(State):
    def __init__(self, dataset_zip: Union[str, BinaryIO]):
        if isinstance(dataset_zip, str) and (
            dataset_zip.startswith("http://") or dataset_zip.startswith("https://")
        ):
            dataset_zip, _headers = urlretrieve(dataset_zip)  # nosec B310

        from solidago.state import Users, Vouches, Entities, Privacy, Comparisons, Judgments, VotingRights, UserModels, DirectScoring
        with zipfile.ZipFile(dataset_zip) as zip_file:
            def load(filename, columns):
                with (zipfile.Path(zip_file) / f"{filename}.csv").open(mode="rb") as f:
                    # keep_default_na=False is required otherwise some public usernames
                    # such as "NA" are converted to float NaN.
                    return pd.read_csv(f, keep_default_na=False).rename(columns=columns)
                
            users = Users(load("users", { "public_username": "username" }))
            pd_vouches = load("vouchers", { "by_username": "by", "to_username": "to", "value": "weight" })
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
            pd_user_scores = load("individual_criteria_scores", { 
                "criteria": "criterion", 
                "video": "entity_id",
                "public_username": "username"
            })
        
        pd_user_scores["depth"] = 0
        pd_global_scores["depth"] = 0
        
        entities = Entities({ "entity_id": list(set(pd_global_scores["entity_id"])) })
        pd_vouches["kind"] = "ProofOfPersonhood"
        vouches = Vouches(pd_vouches)
            
        # All interactions of Tournesol's public dataset are public
        privacy = Privacy()
        for _, r in pd_user_scores.iterrows():
            privacy[r["username"], r["entity_id"]] = False
        
        voting_rights_columns = ["username", "entity_id", "criterion", "voting_right"]
        voting_rights = VotingRights(pd_user_scores[voting_rights_columns])

        user_models_instructions = { user.name: ["DirectScoring", dict()] for user in users }
        user_models = UserModels.load(user_models_instructions, pd_user_scores, DataFrame())
        
        global_model = DirectScoring.load(dict(), pd_global_scores, DataFrame())
        
        super().__init__(users, vouches, entities, voting_rights, judgments, user_models, global_model)
        self.criteria = {
            "reliability": "Reliable and not misleading",
            "importance": "Important and actionable",
            "engaging": "Engaging and thought-provoking",
            "pedagogy": "Clear and pedagogical",
            "layman_friendly": "Layman-friendly",
            "diversity_inclusion": "Diversity and inclusion",
            "backfire_risk": "Resilience to backfiring risks",
            "better_habits": "Encourages better habits",
            "entertaining_relaxing": "Entertaining and relaxing"
        }

    @classmethod
    def download(cls) -> "TournesolDataset":
        return cls(dataset_zip="https://api.tournesol.app/exports/all")

    def get_comparisons(self, criterion=None, user_id=None) -> DataFrame:
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
        user_entities_pairs = Series(
            iter(
                set(self.comparisons.groupby(["user_id", "entity_a"]).indices.keys())
                | set(self.comparisons.groupby(["user_id", "entity_b"]).indices.keys())
            )
        )
        dtf = DataFrame([*user_entities_pairs], columns=["user_id", "entity_id"])
        dtf["is_public"] = True
        return dtf

    def get_individual_scores(
        self,
        user_id: Optional[int] = None,
        criterion: Optional[str] = None,
        with_n_comparisons=False,
    ) -> DataFrame:
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
    ) -> DataFrame:
        dtf: DataFrame = self.collective_scores
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
        return DataFrame(
            {
                "voucher": vouchers.by_username.map(self.username_to_user_id),
                "vouchee": vouchers.to_username.map(self.username_to_user_id),
                "vouch": vouchers.value,
            }
        )

    def get_users(self):
        users_df = DataFrame(
            {
                "trust_score": self.users["trust_score"],
            },
            index=self.users.index,
        )
        # TODO: export pretrusted status in public dataset
        users_df["is_pretrusted"] = users_df["trust_score"] >= 0.8
        return users_df
