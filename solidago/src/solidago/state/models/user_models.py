from typing import Union, Optional, Iterable
from pathlib import Path
from pandas import DataFrame

import pandas as pd

from .base import ScoringModel
from .score import MultiScore
from .direct import DirectScoring


class UserModels(dict):
    """ dfs is the set of dataframes that are loaded/saved to reconstruct a scoring model """
    df_names: set[str]={ "user_directs", "user_scalings" }
    
    def __init__(self, model_cls: type=DirectScoring, *args, **kwargs):
        """ Maps usernames to ScoringModel objects.
        Useful to export/import `glued` directs / scalings dataframes. """
        super().__init__(*args, **kwargs)
        self.model_cls = model_cls

    def default_value(self) -> ScoringModel:
        return self.model_cls()

    def score(self, entity: Union[str, "Entity", "Entities"]) -> MultiScore:
        from solidago.state import Entity, Entities
        if isinstance(entity, (str, Entity)):
            result = NestedDictOfTuples(key_names=["username", "criterion"])
            for username, model in self:
                multiscore = model(entity)
                for criterion, score in multiscore:
                    result[username, criterion] = score.to_triplet()
            return result
        assert isinstance(entity, Entities)
        entities = entity
        result = NestedDictOfTuples(key_names=["username", "entity_name", "criterion"])
        for username, model in self:
            for entity in model.evaluated_entities(entities):
                multiscore = model(entity)
                for criterion, score in multiscore:
                    result[username, str(entity), criterion] = score.to_triplet()
    
    def __getitem__(self, user: Union[str, "User"]) -> ScoringModel:
        if str(user) not in self.keys():
            return self.default_value()
        return super().__getitem__(str(user))
    
    def __iter__(self) -> Iterable:
        for username, model in self.items():
            yield username, model
    
    @classmethod
    def dfs_load(cls, d: dict, loaded_dfs: Optional[dict]) -> dict[str, dict[str, DataFrame]]:
        if loaded_dfs is None:
            loaded_dfs = dict()
        for df_name in cls.df_names & set(d):
            df = pd.read_csv(d[df_name], keep_default_na=False)
            for _, r in df.iterrows():
                if r["username"] not in loaded_dfs:
                    loaded_dfs[r["username"]] = dict()
                if df_name not in loaded_dfs[r["username"]]:
                    loaded_dfs[r["username"]][df_name] = list()
                loaded_dfs[r["username"]][df_name].append(r)
        return {
            username: {
                df_name: DataFrame(rows_list)
                for df_name, rows_list in loaded_dfs[username].items()
            } for username in loaded_dfs
        }       
    
    @classmethod
    def load(cls, d: dict, dfs: Optional[dict[str, dict[str, DataFrame]]]=None) -> "UserModels":
        if "users" not in d:
            return cls()
        import solidago.state.models as models
        if "dataframes" in d:
            dfs = cls.dfs_load(d["dataframes"], dfs)
        def user_dfs(username):
            if dfs is None or username not in dfs:
                return dict()
            return { df_name.split("_")[-1]: df for df_name, df in dfs[username].items() }
        return cls(getattr(models, d["model_cls"]), {
            username: getattr(models, user_d[0]).load(user_d[1], user_dfs(username))
            for username, user_d in d["users"].items()
        })
    
    def to_dfs(self) -> dict[str, DataFrame]:
        dfs = { df_name: self.export_df(df_name) for df_name in self.df_names }
        return { df_name: df for df_name, df in dfs.items() if not df.empty }
        
    def export_df(self, df_name: str) -> DataFrame:
        user_df_name = df_name.split("_")[-1]
        return DataFrame(sum([
            [ dict(username=username) | dict(r) for _, r in model.export_df(user_df_name).iterrows() ]
            for username, model in self
        ], list()))

    def save(self, directory: Union[Path, str], json_dump: bool=False) -> tuple[str, dict, dict]:
        df_filenames = dict()
        for df_name in self.df_names:
            df = self.export_df(df_name)
            if df.empty:
                continue
            filename = Path(directory) / f"{df_name}.csv"
            df.to_csv(filename, index=False)
            df_filenames[df_name] = str(filename)
        j = type(self).__name__, {
            "users": { username: model.save() for username, model in self },
            "dataframes": df_filenames,
            "model_cls": self.model_cls.__name__,
        }, 
        if json_dump:
            with open(directory / "user_models.json", "w") as f:
                json.dump(j, f)
        return j

    def __repr__(self) -> str:
        return "\n\n".join([repr(df) for df in self.to_dfs().values()])
