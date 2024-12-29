from typing import Union, Optional
from pathlib import Path
from pandas import DataFrame

import pandas as pd

from solidago.primitives.datastructure.nested_dict import NestedDict
from .base import ScoringModel


class UserModels(NestedDict):
    """ dfs is the set of dataframes that are loaded/saved to reconstruct a scoring model """
    df_names: set[str]={ "user_directs", "user_scalings" }
    
    def __init__(self, 
        d: Optional[Union[NestedDict, dict, DataFrame]]=None,
        key_names: list[str]=["username"], 
        value_names: Optional[list[str]]=None,
        save_filename: Optional[str]=None,
        model_cls: type=ScoringModel,
    ):
        """ Maps usernames to ScoringModel objects.
        Useful to export/import `glued` directs / scalings dataframes. """
        super().__init__(d=d, key_names=key_names, value_names=value_names, save_filename=None)
        self.model_cls = model_cls
    
    @classmethod
    def dfs_load(cls, d: dict, loaded_dfs: dict) -> dict[str, dict[str, DataFrame]]:
        if loaded_dfs is None:
            loaded_dfs = dict()
        for df_name in cls.df_names & set(d):
            df = pd.read_csv(d[df_name], keep_default_na=False)
            for _, r in df.iterrows():
                if r["username"] not in loaded_dfs:
                    loaded_dfs[r["username"]] = dict()
                if df_name not in loaded_dfs[r["username"]]:
                    loaded_dfs[df_name][r["username"]] = list()
                loaded_dfs[df_name][r["username"]].append(r)
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
        return cls({
            username: getattr(models, user_d[0]).load(user_d[1], dfs[username] if username in dfs else dict())
            for username, user_d in d["users"].items()
        })
    
    def to_dfs(self) -> dict[str, DataFrame]:
        dfs = { df_name: self.to_df(df_name) for df_name in self.df_names }
        return { df_name: df for df_name, df in dfs.items() if not df.empty }
        
    def to_df(self, df_name: str) -> DataFrame:
        return DataFrame(sum([
            [ dict(username=username) | dict(r) for _, r in model.to_df(df_name).iterrows() ]
            for username, model in self
        ], list()))

    def save(self, directory: Union[Path, str], json_dump: bool=False) -> tuple[str, dict, dict]:
        df_filenames = dict()
        for df_name in self.df_names:
            df = self.to_df(df_name)
            if df.empty:
                continue
            filename = Path(directory) / f"{df_name}.csv"
            df.to_csv(filename, index=False)
            df_filenames[df_name] = str(filename)
        j = type(self).__name__, {
            "users": { username: model.save() for username, model in self },
            "dataframes": df_filenames
        }
        if json_dump:
            with open(directory / "user_models.json", "w") as f:
                json.dump(j, f)
        return j

    def __setitem__(self, user: Union[str, "User"], model: "ScoringModel") -> None:
        self._dict[str(user)] = model
    
    def __getitem__(self, user: "User") -> "ScoringModel":
        return self._dict[str(user)]
        
    def __iter__(self):
        for key_value in self._dict.items():
            yield key_value
            
    def __contains__(self, user: Union[str, "User"]) -> bool:
        return str(user) in self._dict

    def __repr__(self) -> str:
        return "\n\n".join(self.to_dfs().values())
