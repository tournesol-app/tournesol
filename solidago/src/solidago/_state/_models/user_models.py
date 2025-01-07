from typing import Union, Optional, Iterable
from pathlib import Path
from pandas import DataFrame

import pandas as pd

from .base import ScoringModel
from .score import MultiScore
from .direct import DirectScoring


class UserModels(dict):
    def __init__(self, *args, default_model_cls: type=DirectScoring, **kwargs):
        """ Maps usernames to ScoringModel objects.
        Useful to export/import `glued` directs / scalings dataframes. """
        super().__init__(*args, **kwargs)
        self.default_model_cls = default_model_cls

    def default_value(self) -> ScoringModel:
        return self.default_model_cls()

    def score(self, entity: Union[str, "Entity", "Entities"]) -> MultiScore:
        from solidago._state._entities import Entity, Entities
        if isinstance(entity, (str, Entity)):
            result = MultiScore(key_names=["username", "criterion"])
            for username, model in self:
                multiscore = model(entity)
                for criterion, score in multiscore:
                    result[username, criterion] = score
            return result
        assert isinstance(entity, Entities)
        entities = entity
        result = MultiScore(key_names=["username", "entity_name", "criterion"])
        for username, model in self:
            for entity in model.evaluated_entities(entities):
                multiscore = model(entity)
                for criterion, score in multiscore:
                    result[username, str(entity), criterion] = score
        return result
    
    def __getitem__(self, user: Union[str, "User"]) -> ScoringModel:
        if str(user) not in self.keys():
            return self.default_value()
        return super().__getitem__(str(user))
    
    def __setitem__(self, user: Union[str, "User"], model: ScoringModel) -> None:
        super().__setitem__(str(user), model)
    
    def __contains__(self, user: Union[str, "User"]) -> bool:
        return super().__contains__(str(user))
    
    def __iter__(self) -> Iterable:
        for username, model in self.items():
            yield username, model
    
    @classmethod
    def dfs_load(cls, d: dict, loaded_dfs: Optional[dict]) -> dict[str, dict[str, DataFrame]]:
        if loaded_dfs is None:
            loaded_dfs = dict()
        for df_name in set(d):
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
        import solidago._state._models as models
        if "dataframes" in d:
            dfs = cls.dfs_load(d["dataframes"], dfs)
        def user_dfs(username):
            if dfs is None or username not in dfs:
                return dict()
            return { df_name.split("_")[-1]: df for df_name, df in dfs[username].items() }
        kwargs = dict()
        if "default_model_cls" in d:
            kwargs |= dict(default_model_cls=getattr(models, d["default_model_cls"]))
        return cls({
            username: getattr(models, user_d[0]).load(user_d[1], user_dfs(username))
            for username, user_d in d["users"].items()
        }, **kwargs)
    
    def to_dfs(self) -> dict[str, DataFrame]:
        return { df_name: DataFrame(rows) for df_name, rows in self.to_rows().items() }
        
    def to_rows(self, depth: int=0) -> dict[str, list]:
        """ Must return a dict, with df_name as keys, and a list of rows as values """
        rows = dict()
        for username, model in self:
            for key_name, user_rows in model.to_rows(depth=0, kwargs=dict(username=username)).items():
                if key_name not in rows:
                    rows[key_name] = list()
                rows[key_name] += user_rows
        return rows

    def save(self, directory: Union[Path, str]=None, json_dump: bool=False) -> tuple[str, dict]:
        assert isinstance(directory, (Path, str)), directory
        df_filenames = dict()
        for df_name, df in self.to_dfs().items():
            if df.empty:
                continue
            filename = Path(directory) / f"user_{df_name}.csv"
            df.to_csv(filename, index=False)
            df_filenames[df_name] = str(filename)
        j = type(self).__name__, {
            "users": { username: model.save() for username, model in self },
            "dataframes": df_filenames,
            "default_model_cls": self.default_model_cls.__name__,
        }, 
        if json_dump:
            with open(directory / "user_models.json", "w") as f:
                json.dump(j, f)
        return j

    def __repr__(self) -> str:
        return "\n\n".join([repr(df) for df in self.to_dfs().values()])
