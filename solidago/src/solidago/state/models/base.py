from abc import abstractmethod, ABC
from typing import Optional, Union, Any
from pathlib import Path
from pandas import DataFrame

import pandas as pd
import logging

logger = logging.getLogger(__name__)

from .score import Score, MultiScore


class ScoringModel(ABC):
    saved_argsnames: list[str]=["note"]
    
    def __init__(self, 
        dataframes: Optional[dict[str, DataFrame]]=None, 
        depth: int=0, 
        note: str="None",
        *args, 
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.depth = depth
        self.note = note
        self.dfs = dict() if dataframes is None else dataframes
        for name, df in self.dfs.items():
            if isinstance(df, (str, Path)):
                df_filename = df
                try: df = pd.read_csv(df_filename, keep_default_na=False)
                except pd.errors.EmptyDataError: df = DataFrame()
                self.dfs[name] = df
            if name == "directs":
                self.dfs[name] = MultiScore(df, key_names=["entity_name", "criterion"])
            elif name == "multiplicators" and isinstance(df, DataFrame):
                self.dfs[name] = MultiScore(df, key_names=["depth", "criterion"]).groupby(["depth"])
            elif name == "translations" and isinstance(df, DataFrame):
                self.dfs[name] = MultiScore(df, key_names=["depth", "criterion"]).groupby(["depth"])
        if "parent" in kwargs:
            if isinstance(kwargs["parent"], ScoringModel):
                self.parent = kwargs["parent"]
            elif isinstance(kwargs["parent"], ScoringModel):
                import solidago.state.models as models
                parent_cls, parent_kwargs = kwargs["parent"]
                self.parent = getattr(models, parent_cls)(self.dfs, depth + 1, **parent_kwargs)
            else:
                raise ValueError(f"{kwargs['parent']} has unhandled type {type(kwargs['parent'])}")

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
            results = MultiScore(key_names=["entity_name", "criterion"])
            for entity in entities:
                for criterion, score in self(entity):
                    results.add_row([ str(entity), criterion, *score.to_triplet() ])
            return results
        entity = entities
        return self.score(entity)
    
    @abstractmethod
    def score(self, entity: "Entity") -> MultiScore:
        raise NotImplementedError
    
    def is_base(self) -> bool:
        return not hasattr(self, parent)
    
    def evaluated_entities(self, entities: "Entities") -> "Entities":
        return entities if self.is_base() else self.parent.evaluated_entities(entities)
    
    def to_direct(self, entities: "Entities") -> "DirectScoring":
        from .direct import DirectScoring
        direct_scoring = DirectScoring()
        for entity in entities:
            for criterion, score in self(entity):
                if not score.isnan():
                    direct_scoring[entity, criterion] = score
        return direct_scoring
        
    def saved_kwargs(self) -> dict:
        kwargs = { name: getattr(self, name) for name in self.saved_argsnames }
        if not self.is_base():
            kwargs["parent"] = self.parent.saved_kwargs()
        return kwargs

    def save(self, filename: Optional[Union[str, Path]]=None) -> tuple[str, dict]:
        """ save must be given a filename_root (typically without extension),
        as multiple csv files may be saved, with a name derived from the filename_root
        (in addition to the json description) """
        kwargs = self.saved_kwargs()
        if depth > 0 or filename is None:
            return type(self).__name__, kwargs
        if filename is not None:
            assert str(filename)[-5:] == ".json", filename
            directory = "/".join(filename.split("/")[:-1])
            kwargs["dataframes"] = dict()
            for df_name, df in dfs.items():
                save_filename = f"{directory}/{df_name}.csv"
                df.to_csv(save_filename, index=False)
                kwargs["dataframes"][df_name] = save_filename
            with open(filename, "w") as f:
                json.dump([type(self).__name__, saved_dict], f, indent=4)
        return type(self).__name__, kwargs
    
    def base_model(self) -> "BaseModel":
        return self if self.is_base() else self.parent.base_model()

    def __str__(self) -> str:
        return type(self).__name__
    
    def __repr__(self) -> str:
        return type(self).__name__ + "\n\n" + "\n\n".join([
            f"{df_name}\n{repr(df)}" for df_name, df in self.dfs.items() if not df.empty
        ])
