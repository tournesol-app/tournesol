from typing import Union, Optional
from pathlib import Path
from pandas import DataFrame

import pandas as pd


class UserModels:
    def __init__(self, d: Optional[dict]=None):
        self._dict = dict()

    @staticmethod
    def direct_scores_to_dict(direct_scores: DataFrame) -> dict:
        """ Constructs a dict that maps username to DirectScoring """
        from solidago.state.models import DirectScoring, Score
        direct_scores_dict = dict()
        asymmetric = "left_unc" in direct_scores.columns
        left, right = ("left_unc", "right_unc") if asymmetric else ("uncertainty", "uncertainty")
        for _, r in direct_scores.iterrows():
            if r["username"] not in direct_scores_dict:
                direct_scores_dict[r["username"]] = list()
            direct_scores_dict[r["username"]].append(r)
        return { username: DataFrame(direct_scores_dict[username]) for username in direct_scores_dict }

    @staticmethod
    def scalings_df_to_scaling_parameters(scalings_df: DataFrame) -> dict:
        """ out[username][depth][criterion] yields the multiplicator and the translation (Score) """
        from solidago.state.models import Score
        scaling_params = dict()
        for _, r in scalings_df.iterrows():
            username, criterion, depth = r["username"], r["criterion"], r["depth"]
            if username not in scaling_params:
                scaling_params[username] = dict()
            if depth not in scaling_params[username]:
                scaling_params[username][depth] = dict()
            scaling_params[username][depth][criterion] = [
                Score(r["multiplicator_score"], r["multiplicator_left"], r["multiplicator_right"]),
                Score(r["translation_score"], r["translation_left"], r["translation_right"])
            ]
        return scaling_params

    @classmethod
    def load(cls, d: dict, direct_scores: DataFrame, scalings_df: DataFrame):
        import solidago.state.models as models
        direct_scores_dict = UserModels.direct_scores_to_dict(direct_scores)
        scaling_params = UserModels.scalings_df_to_scaling_parameters(scalings_df)
        user_models = cls()
        for username in d:
            model_cls = getattr(models, d[username][0])
            user_direct_scores = direct_scores_dict[username] if username in direct_scores_dict else DataFrame()
            user_scaling = scaling_params[username] if username in scaling_params else dict()
            user_models[username] = model_cls.load(d[username][1], user_direct_scores, user_scaling)
        return user_models
    
    def save_scalings(self, filename: Union[Path, str]) -> DataFrame:
        filename, rows, sub_df = Path(filename), list(), DataFrame()
        for username, model in self:
            sub_df = model.scalings_df()
            rows += [[username] + r.values.flatten().tolist() for _, r in sub_df.iterrows()]
        columns = ["username"] + sub_df.columns
        df = DataFrame(rows, columns=columns)
        df.to_csv(filename)
        return df

    def save_direct_scores(self, filename: Union[Path, str]) -> DataFrame:
        from .direct import DirectScoring
        filename, rows, sub_df = Path(filename), list(), DataFrame()
        for username, model in self:
            foundation_model, depth = model.foundational_model()
            if not isinstance(foundation_model, DirectScoring):
                continue
            sub_df = foundation_model.to_df(depth)
            rows += [[username] + r.values.flatten().tolist() for _, r in sub_df.iterrows()]
        columns = ["username"] + list(sub_df.columns)
        df = DataFrame(rows, columns=columns)
        df.to_csv(filename)
        return df

    def save(self, directory: Union[Path, str]) -> Union[str, list, dict]:
        directory = Path(directory)
        return type(self).__name__, {
            username: model.to_dict(data=False)
            for username, model in self
        }        
            
    def __setitem__(self, user: Union[int, str, "User"], model: "ScoringModel"):
        self._dict[user if isinstance(user, (int, str)) else user.name] = model
    
    def __getitem__(self, user: "User"):
        return self._dict[user if isinstance(user, (int, str)) else user.name]
        
    def __iter__(self):
        for key_value in self._dict.items():
            yield key_value
            
