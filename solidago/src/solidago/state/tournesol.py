import zipfile
from functools import cached_property
from typing import BinaryIO, Optional, Union
from urllib.request import urlretrieve
from pandas import DataFrame, Series

import pandas as pd

from .base import *


class TournesolExport(State):
    @staticmethod
    def load_dfs(dataset_zip: Union[str, BinaryIO]) -> dict[str, DataFrame]:
        if isinstance(dataset_zip, str) and (
            dataset_zip.startswith("http://") or dataset_zip.startswith("https://")
        ):
            dataset_zip, _headers = urlretrieve(dataset_zip)  # nosec B310

        with zipfile.ZipFile(dataset_zip) as zip_file:
            def load(filename, columns):
                with (zipfile.Path(zip_file) / f"{filename}.csv").open(mode="rb") as f:
                    # keep_default_na=False is required otherwise some public usernames
                    # such as "NA" are converted to float NaN.
                    return pd.read_csv(f, keep_default_na=False).rename(columns=columns)
                
            users = load("users", { "public_username": "username" })
            vouches = load("vouchers", { 
                "by_username": "by", 
                "to_username": "to", 
                "value": "weight" 
            })
            comparisons = load("comparisons", { 
                "public_username": "username",
                "video_a": "left_name",
                "video_b": "right_name",
                "criteria": "criterion_name",
                "score": "comparison",
                "score_max": "comparison_max"
            })
            global_scores = load("collective_criteria_scores", { 
                "criteria": "criterion_name", 
                "video": "entity_name",
            })
            user_scores = load("individual_criteria_scores", { 
                "criteria": "criterion_name", 
                "video": "entity_name",
                "public_username": "username"
            })
        
        vouches["kind"] = "Personhood"
        vouches["priority"] = 0
        user_scores["depth"] = 0
        global_scores["depth"] = 0
        from solidago.primitives.date import week_date_to_week_number as to_week_number
        comparisons["week_number"] = [to_week_number(wd) for wd in list(comparisons["week_date"])]
        
        entities = DataFrame({ "entity_name": list(set(global_scores["entity_name"])) })
        criteria = DataFrame([
            ["reliability", "Reliable and not misleading"],
            ["importance", "Important and actionable"],
            ["engaging", "Engaging and thought-provoking"],
            ["pedagogy", "Clear and pedagogical"],
            ["layman_friendly", "Layman-friendly"],
            ["diversity_inclusion", "Diversity and inclusion"],
            ["backfire_risk", "Resilience to backfiring risks"],
            ["better_habits", "Encourages better habits"],
            ["entertaining_relaxing", "Entertaining and relaxing"]
        ], columns=["criterion_name", "description"])
        
        return { "users": users, "vouches": vouches, "entities": entities, "criteria": criteria,
            "comparisons": comparisons, "user_scores": user_scores, "global_scores": global_scores }
    
    def __init__(self, dataset_zip: Union[str, BinaryIO]):
        dfs = TournesolExport.load_dfs(dataset_zip)
        from solidago.state import Users, Vouches, Entities, AllPublic, Comparisons, VotingRights, UserModels, DirectScoring
        voting_rights_columns = ["username", "entity_name", "criterion_name", "voting_right"]
        user_models_instructions = { username: ["DirectScoring", dict()] for username in dfs["users"]["username"] }
        super().__init__(
            users=Users(dfs["users"]),
            vouches=Vouches(dfs["vouches"]),
            entities=Entities(dfs["entities"]),
            criteria=Criteria(dfs["criteria"]),
            made_public=AllPublic(),
            comparisons=Comparisons(dfs["comparisons"]),
            voting_rights = VotingRights(dfs["user_scores"][voting_rights_columns]),
            user_models=UserModels.load(user_models_instructions, dfs["user_scores"], DataFrame()),
            global_model=DirectScoring.load(dict(), dfs["global_scores"], DataFrame())
        )

    @classmethod
    def download(cls) -> "TournesolExport":
        return cls(dataset_zip="https://api.tournesol.app/exports/all")

