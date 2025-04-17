from typing import BinaryIO, Optional, Union
from urllib.request import urlretrieve
from pandas import DataFrame, Series

import zipfile
import pandas as pd
import numpy as np

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
                
            users = load("users", { "public_username": "username", "trust_score": "trust" })
            vouches = load("vouchers", { 
                "by_username": "by", 
                "to_username": "to", 
                "value": "weight" 
            })
            comparisons = load("comparisons", { 
                "public_username": "username",
                "video_a": "left_name",
                "video_b": "right_name",
                "criteria": "criterion",
                "score": "value",
                "score_max": "max"
            })
            global_scores = load("collective_criteria_scores", { 
                "criteria": "criterion", 
                "video": "entity_name",
                "score": "value",
                "uncertainty": "left_unc",
            })
            user_scores = load("individual_criteria_scores", { 
                "criteria": "criterion", 
                "video": "entity_name",
                "public_username": "username",
                "score": "squashed_value",
                "uncertainty": "squashed_left_unc",                
            })
        
        missing_usernames = set(vouches["by"]) | set(vouches["to"]) | set(user_scores["username"])
        missing_usernames = missing_usernames.difference(set(users["username"]))
        for username in missing_usernames:
            users.loc[len(users)] = [username, 0.]

        users["is_pretrusted"] = pd.to_numeric(users["trust"]) >= 0.8
        vouches["kind"] = "Personhood"
        vouches["priority"] = 0
        user_scores["depth"] = 0
        global_scores["depth"] = 0
        unsquash = lambda x: np.clip(x, a_min=-99.9, a_max=99.9) / np.sqrt(100**2 - np.clip(x, a_min=-99.9, a_max=99.9)**2)
        user_scores["value"] = unsquash(user_scores["squashed_value"])
        max_values = user_scores["squashed_value"] + user_scores["squashed_left_unc"]
        user_scores["left_unc"] = unsquash(max_values) - user_scores["value"]
        user_scores["right_unc"] = user_scores["left_unc"]
        global_scores["right_unc"] = global_scores["left_unc"]
        from solidago.primitives.date import week_date_to_week_number as to_week_number
        comparisons["week_number"] = [to_week_number(wd) for wd in list(comparisons["week_date"])]
                
        entities = DataFrame({ "entity_name": list(
            set(global_scores["entity_name"]) | set(comparisons["left_name"]) | set(comparisons["right_name"])
        ) })
        voting_rights = user_scores[["username", "entity_name", "criterion", "voting_right"]]
        
        return dict(users=users, vouches=vouches, entities=entities, comparisons= comparisons, 
            voting_rights=voting_rights, user_scores=user_scores, global_scores=global_scores)
    
    def __init__(self, dataset_zip: Union[str, BinaryIO]):
        dfs = TournesolExport.load_dfs(dataset_zip)
        from solidago.state import (
            Users, Vouches, Entities, AllPublic, Comparisons, 
            VotingRights, UserModels, ScoringModel, MultiScore
        )
        user_directs = MultiScore(UserModels.table_keynames["user_directs"], dfs["user_scores"])
        directs = MultiScore(["entity_name", "criterion"], dfs["global_scores"])
        super().__init__(
            users=Users(dfs["users"]),
            vouches=Vouches(init_data=dfs["vouches"]),
            entities=Entities(dfs["entities"]),
            made_public=AllPublic(),
            comparisons=Comparisons(init_data=dfs["comparisons"]),
            voting_rights=VotingRights(init_data=dfs["voting_rights"]),
            user_models=UserModels(user_directs=user_directs),
            global_model=ScoringModel(directs=directs)
        )

    @classmethod
    def download(cls) -> "TournesolExport":
        return cls(dataset_zip="https://api.tournesol.app/exports/all")

