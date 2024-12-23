from typing import Union
from pathlib import Path

import pandas as pd


class UserModels:
    def __init__(self, d: dict=dict()):
        self._dict = d
        self.iterator = None

    @staticmethod
    def direct_scores_to_direct_models(direct_scores: pd.DataFrame) -> dict[str, "DirectScoring"]:
        """ Constructs a dict that maps username to DirectScoring """
        from solidago.state.models import DirectScoring, Score
        direct_models = dict()
        asymmetric = "left_unc" in direct_scores.columns
        left, right = ("left_unc", "right_unc") if asymmetric else ("uncertainty", "uncertainty")
        for _, r in direct_scores.iterrows():
            if r["username"] not in direct_models:
                direct_models[r["username"]] = DirectScoring()
            direct_models[r["username"]][r["entity_id"], r["criterion"]] = Score(r["score"], r[left], r[right])
        return direct_models

    @staticmethod
    def scalings_df_to_scaling_parameters(scalings_df: pd.DataFrame) -> dict:
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
    def load(cls, d: dict, direct_scores: pd.DataFrame, scalings_df: pd.DataFrame=pd.DataFrame()):
        import solidago.state.models as models
        direct_models = UserModels.direct_scores_to_direct_models(direct_scores)
        scaling_params = UserModels.scalings_df_to_scaling_parameters(scalings_df)
        user_models = cls()
        for u in d:
            model_cls = getattr(models, d[u][0])
            user_scaling = scaling_params[u] if u in scaling_params else dict()
            user_models[u] = model_cls.load(d[u][1], direct_models[u], user_scaling)
        return user_models
    
    def save_scalings(self, filename: Union[Path, str]) -> pd.DataFrame:
        filename = Path(filename)
        df = pd.DataFrame(columns=["username", "criterion", "depth",
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

    def save_direct_scores(self, filename: Union[Path, str]) -> pd.DataFrame:
        filename = Path(filename)
        df = pd.DataFrame(columns=["username", "entity_id", "criterion", "depth",
            "score", "left_uncertainty", "right_uncertainty"])
        from .direct import DirectScoring
        
        for user, model in self:
            foundation_model, depth = model.foundational_model()    
            if not isinstance(foundation_model, DirectScoring):
                continue
            for entity in foundational_model.scored_entities(entities=None):
                scores = foundation_model(entity)
                for criterion, s in scores.items():
                    df.iloc[-1] = [ user.name, entity.id, criterion, depth, s.value, s.left, s.right]
            
        df.to_csv(filename)
        return df

    def save(self, directory: Union[Path, str]) -> Union[str, list, dict]:
        directory = Path(directory)
        self.save_scalings(directory / "scaling.csv")
        self.save_direct_scores(directory / "direct_scores.csv")
        return {
            "scaling": str(directory / "scaling.csv"),
            "direct_score": str(directory / "direct_scores.csv"),
            "users": {
                user.id: model.to_dict(data=False)
                for user, model in self
            }
        }        
            
    def __setitem__(self, user: Union[str, "User"], model: "ScoringModel"):
        self._dict[user if isinstance(user, str) else user.name] = model
    
    def __getitem__(self, user: "User"):
        return self._dict[user]
        
    def __iter__(self):
        iterator = self._dict.items()
        while True:
            try: yield next(iterator)
            except StopIteration: break
            
