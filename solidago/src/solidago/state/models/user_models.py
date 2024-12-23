from typing import Union, Optional
from pathlib import Path
from pandas import DataFrame


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
        return { username: DataFrame(direct_scores_dict[r["username"]]) for username in direct_scores_dict }

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
        filename = Path(filename)
        df = DataFrame(columns=["username", "criterion", "depth",
            "multiplicator_score", "multiplicator_left", "multiplicator_right", 
            "translation_score", "translation_left", "translation_right"])
        for user, model in self:
            base_model, depth = model, 0
            while hasattr(base_model, "base_model"):
                if not isinstance(base_model, ScaledModel):
                    continue
                for criterion in self.scaled_criteria():
                    m = base_model.multiplicator(criterion)
                    t = base_model.translation(criterion)
                    df.iloc[-1] = [user.name, criterion, depth, m.value, m.left, m.right, t.value, t.left, t.right]
                depth += 1
                base_model = base_model.base_model
        df.to_csv(filename)
        return df

    def save_direct_scores(self, filename: Union[Path, str]) -> DataFrame:
        filename = Path(filename)
        from .direct import DirectScoring
        direct_scores = list()
        
        for username, model in self:
            foundation_model, depth = model.foundational_model()
            if not isinstance(foundation_model, DirectScoring):
                continue
            for entity in foundation_model.scored_entities(entities=None):
                scores = foundation_model(entity)
                for criterion, s in scores.items():
                    direct_scores.append({
                        "username": username, 
                        "entity_id": entity.id, 
                        "criterion": criterion, 
                        "depth": depth, 
                        "score": s.value, 
                        "left_unc": s.left, 
                        "right_unc": s.right
                    })
        df = DataFrame(direct_scores)
        df.to_csv(filename)
        return df

    def save(self, directory: Union[Path, str]) -> Union[str, list, dict]:
        directory = Path(directory)
        return type(self).__name__, {
            user.id: model.to_dict(data=False)
            for user, model in self
        }        
            
    def __setitem__(self, user: Union[str, "User"], model: "ScoringModel"):
        self._dict[user if isinstance(user, str) else user.name] = model
    
    def __getitem__(self, user: "User"):
        return self._dict[user]
        
    def __iter__(self):
        for key_value in self._dict.items():
            yield key_value
            
