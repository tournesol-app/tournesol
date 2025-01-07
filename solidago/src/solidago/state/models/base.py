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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
            
    def __call__(self, entities: Union["Entity", "Entities"]) -> MultiScore:
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
            return MultiScore(
                { entity: self(entity) for entity in entities },
                key_names=["entity_name", "criterion"]
            )
        entity = entities
        return self.score(entity)
    
    @abstractmethod
    def score(self, entity: "Entity") -> MultiScore:
        raise NotImplementedError
    
    def evaluated_entities(self, entities: "Entities") -> "Entities":
        return self.parent.evaluated_entities(entities)
    
    @classmethod
    def dfs_load(cls, d: dict[str, Any], loaded_dfs: Optional[dict[str, DataFrame]]=None) -> dict[str, DataFrame]:
        if loaded_dfs is None:
            loaded_dfs = dict()
        for df_name in set(d):
            if df_name == "parent":
                continue
            assert isinstance(d[df_name], str), (df_name, d)
            if df_name in loaded_dfs:
                logger.warn("Multiple scaling model dataframe loading. Overriding the previously loaded.")
            try: loaded_dfs[df_name] = pd.read_csv(d[df_name], keep_default_na=False)
            except pd.errors.EmptyDataError: loaded_dfs[df_name] = DataFrame()
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

    def save(self, directory: Optional[str]=None, depth: int=0, json_dump: bool=False) -> tuple[str, dict]:
        """ save must be given a filename_root (typically without extension),
        as multiple csv files may be saved, with a name derived from the filename_root
        (in addition to the json description) """
        if depth > 0 or directory is None:
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
            save_filename = f"{directory}/{df_name}.csv"
            df.to_csv(save_filename, index=False)
            saved_dict[df_name] = save_filename
        if json_dump:
            with open(f"{directory}/model.json", "w") as f:
                json.dump([type(self).__name__, saved_dict], f, indent=4)
        return type(self).__name__, saved_dict
    
    def to_dfs(self, depth: int=0, kwargs: Optional[dict]=None) -> dict[str, DataFrame]:
        return { df_name: DataFrame(rows) for df_name, rows in self.to_rows(depth, kwargs).items() }
        
    def to_rows(self, depth: int=0, kwargs: Optional[dict]=None) -> dict[str, list]:
        """ Must return a dict, with df_name as keys, and a list of rows as values """
        return self.parent.to_rows(depth + 1, kwargs)

    def base_model(self, depth: int=0) -> "BaseModel":
        return (self, depth) if isinstance(self, BaseModel) else self.parent.base_model(depth + 1)

    def __str__(self) -> str:
        return type(self).__name__
    
    def __repr__(self) -> str:
        return "\n\n".join([repr(df) for df in self.to_dfs().values() if not df.empty])


class BaseModel(ScoringModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def to_direct(self, entities: "Entities") -> "DirectScoring":
        from .direct import DirectScoring
        direct_scoring = DirectScoring()
        for entity in entities:
            for criterion, score in self(entity):
                if not score.isnan():
                    direct_scoring[entity, criterion] = score
        return direct_scoring

    def evaluated_entities(self, entities: "Entities") -> "Entities":
        return entities

    @abstractmethod
    def to_rows(self, depth: int=0, kwargs: Optional[dict]=None) -> dict[str, list]:
        raise NotImplemented
