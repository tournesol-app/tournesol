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
                
            users_df = load("users", { "public_username": "username" })
            vouches_df = load("vouchers", { "by_username": "by", "to_username": "to", "value": "weight" })
            comparisons_df = load("comparisons", { 
                "public_username": "username",
                "video_a": "left_id",
                "video_b": "right_id",
                "criteria": "criterion",
                "score": "comparison",
                "score_max": "comparison_max"
            })
            global_scores_df = load("collective_criteria_scores", { 
                "criteria": "criterion", 
                "video": "entity_id",
            })
            user_scores_df = load("individual_criteria_scores", { 
                "criteria": "criterion", 
                "video": "entity_id",
                "public_username": "username"
            })
        
        vouches_df["kind"] = "ProofOfPersonhood"
        user_scores_df["depth"] = 0
        global_scores_df["depth"] = 0
        
        users = Users(users_df)
        vouches = Vouches(vouches_df)
        entities = Entities({ "entity_id": list(set(global_scores_df["entity_id"])) })
            
        # All interactions of Tournesol's public dataset are public
        privacy = Privacy()
        for _, r in user_scores_df.iterrows():
            privacy[r["username"], r["entity_id"]] = False
        
        judgments = Judgments(comparisons=Comparisons(comparisons_df))
        
        voting_rights_columns = ["username", "entity_id", "criterion", "voting_right"]
        voting_rights = VotingRights(user_scores_df[voting_rights_columns])

        user_models_instructions = { user.name: ["DirectScoring", dict()] for user in users }
        user_models = UserModels.load(user_models_instructions, user_scores_df, DataFrame())
        
        global_model = DirectScoring.load(dict(), global_scores_df, DataFrame())
        
        super().__init__(users, vouches, entities, privacy, judgments, voting_rights, user_models, global_model)
        
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

