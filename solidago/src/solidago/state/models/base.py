from abc import abstractmethod, ABC
from typing import Optional, Union, Any
from pathlib import Path
from pandas import DataFrame

import pandas as pd
import logging

logger = logging.getLogger(__name__)

from solidago.primitives.datastructure.nested_dict import NestedDict
from .score import Score, MultiScore


class ScoringModel(ABC):
    """ dfs is the set of dataframes that are loaded/saved to reconstruct a scoring model """
    df_names: set[str]={ "directs", "scalings" }
    
    def __call__(self, entities: Union["Entity", "Entities"]) -> Union[MultiScore, NestedDict]:
        """ Assigns a score to an entity, or to multiple entities.
        
        Parameters
        ----------
        entities: Union[Entity, Entities]
            
        Returns
        -------
        out: Score or MultiScore or NestedDict
            If entities: Entity with unidimensional scoring, the output is a Score.
            If entities: Entity with multivariate scoring, then out[criterion_name] is a Score.
            If entities: Entities with unidimensional scoring, then out[entity_name] is a Score.
            If entities: Entities with multivariate scoring, then out[entity_name] is a MultiScore.
        """
        from solidago.state.entities import Entities
        if isinstance(entities, Entities):
            return NestedDict({ entity: self(entity) for entity in entities })
        entity = entities
        return self.score(entity)
    
    @abstractmethod
    def score(self, entity: "Entity") -> MultiScore:
        raise NotImplementedError
    
    @classmethod
    def dfs_load(cls, d: dict[str, Any], loaded_dfs: Optional[dict[str, DataFrame]]=None) -> dict[str, DataFrame]:
        if loaded_dfs is None:
            loaded_dfs = dict()
        for df_name in cls.df_names & set(d):
            assert isinstance(d[df_name], str)
            if df_name in loaded_dfs:
                logger.warn("Multiple scaling model dataframe loading. Overriding the previously loaded.")
            loaded_dfs[df_name] = pd.read_csv(d[df_name], keep_default_na=False)
        return loaded_dfs
    
    @classmethod
    def args_load(cls, d: dict[str, Any], dfs: dict[str, DataFrame], depth: int) -> dict:
        return d["args"] if "args" in d else dict()
    
    @classmethod
    def load(cls, d: dict, dfs: Optional[dict[str, DataFrame]]=None, depth: int=0) -> "ScoringModel":
        import solidago.state.models as models
        dfs = cls.dfs_load(d, dfs)
        args = cls.args_load(d, dfs, depth)
        if "parent" in d:
            base_cls, base_d = d["parent"]
            args["parent"] = getattr(models, base_cls).load(base_d, dfs, depth + 1)
        return cls(**args)

    def args_save(self) -> dict:
        return dict()

    def save(self, filename_root: Optional[str]=None, depth: int=0, json_dump: bool=False) -> tuple[str, dict]:
        """ save must be given a filename_root (typically without extension),
        as multiple csv files may be saved, with a name derived from the filename_root
        (in addition to the json description) """
        if depth > 0 or filename_root is None:
            arg = dict() if isinstance(self, BaseModel) else dict(parent=self.parent.save(depth=depth + 1))
            return type(self).__name__, arg
        dfs = self.to_dfs()
        saved_dict = dict()
        if not isinstance(self, BaseModel):
            saved_dict["parent"] = self.parent.save(depth=depth + 1)
        args = self.args_save()
        if args:
            saved_dict["args"] = args
        for df_name, df in dfs.items():
            save_filename = f"{filename_root}_{df_name}.csv"
            df.to_csv(save_filename, index=False)
            saved_dict[df_name] = save_filename
        if json_dump:
            with open(f"{filename_root}.json", "w") as f:
                json.dump([type(self).__name__, saved_dict], f, indent=4)
        return type(self).__name__, saved_dict
    
    def to_dfs(self) -> dict[str, DataFrame]:
        dfs = { df_name: self.export_df(df_name) for df_name in self.df_names }
        return { df_name: df for df_name, df in dfs.items() if not df.empty }
    
    def export_df(self, df_name: str) -> DataFrame:
        if df_name == "directs":
            return self.directs_df()
        if df_name == "scalings":
            return self.scalings_df()
        raise ValueError(f"{df_name} not known")

    def scalings_df(self) -> DataFrame:
        rows, parent, depth = list(), self, 0
        from .scaled import ScaledModel, MultiScaledModel
        while not isinstance(parent, BaseModel):
            if not isinstance(parent, (ScaledModel, MultiScaledModel)):
                continue
            rows += parent.to_series_list(depth)
            depth += 1
            parent = parent.parent
        return DataFrame(rows)
    
    def directs_df(self) -> Optional[DataFrame]:
        base_model, depth = self.base_model()
        from .direct import DirectScoring
        if isinstance(base_model, DirectScoring):
            return base_model.to_df(depth)
        return DataFrame()
    
    def base_model(self, depth: int=0) -> "BaseModel":
        return (self, depth) if isinstance(self, BaseModel) else self.parent.base_model(depth + 1)

    def __str__(self) -> str:
        return type(self).__name__
    
    def __repr__(self) -> str:
        dfs = [ self.export_df(df_name) for df_name in self.df_names ]
        return "\n\n".join([repr(df) for df in dfs if not df.empty])


class BaseModel(ScoringModel):
    @property
    def parent(self) -> ScoringModel:
        raise ValueError(f"{type(self)} is a BaseModel and thus has no parent")
    
    @abstractmethod
    def to_direct(self) -> "DirectScoring":
        raise NotImplemented
