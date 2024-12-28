from typing import Union, Optional
from pathlib import Path
from pandas import DataFrame

import pandas as pd


class UserModels:
    def __init__(self, d: Optional[dict]=None):
        self._dict = dict()

    @staticmethod
    def direct_scores_to_dict(direct_scores: DataFrame) -> dict[str, DataFrame]:
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
    def scalings_df_to_scaling_parameters(scalings_df: DataFrame) -> dict[str, dict[int, dict[str, tuple["Score", "Score"]]]]:
        """ out[username][depth][criterion] yields the multiplicator and the translation (Score) """
        from solidago.state.models import Score
        scaling_params = dict()
        for _, r in scalings_df.iterrows():
            username, criterion_name, depth = r["username"], r["criterion_name"], r["depth"]
            if username not in scaling_params:
                scaling_params[username] = dict()
            if depth not in scaling_params[username]:
                scaling_params[username][depth] = dict()
            scaling_params[username][depth][criterion_name] = [
                Score(r["multiplicator_score"], r["multiplicator_left"], r["multiplicator_right"]),
                Score(r["translation_score"], r["translation_left"], r["translation_right"])
            ]
        return scaling_params

    @classmethod
    def load(cls, d: dict, direct_scores: DataFrame, scalings_df: DataFrame) -> "UserModels":
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
        columns = ["username"] + list(sub_df.columns)
        df = DataFrame(rows, columns=columns)
        df.to_csv(filename, index=False)
        return df

    def save_direct_scores(self, filename: Union[Path, str]) -> DataFrame:
        from .direct import DirectScoring
        filename, rows, sub_df = Path(filename), list(), DataFrame()
        for username, model in self:
            base_model, depth = model.base_model()
            if not isinstance(base_model, DirectScoring):
                continue
            sub_df = base_model.to_df(depth)
            rows += [[username] + r.values.flatten().tolist() for _, r in sub_df.iterrows()]
        columns = ["username"] + list(sub_df.columns)
        df = DataFrame(rows, columns=columns)
        df.to_csv(filename, index=False)
        return df

    def save(self, directory: Union[Path, str]) -> tuple[str, dict]:
        directory = Path(directory)
        return type(self).__name__, {
            username: model.to_dict(data=False)
            for username, model in self
        }        
            
    def __setitem__(self, user: Union[str, "User"], model: "ScoringModel") -> None:
        self._dict[str(user)] = model
    
    def __getitem__(self, user: "User") -> "ScoringModel":
        return self._dict[str(user)]
        
    def __iter__(self):
        for key_value in self._dict.items():
            yield key_value
            
    def __contains__(self, user: Union[str, "User"]) -> bool:
        return str(user) in self._dict
