from abc import abstractmethod, ABC
from typing import Optional, Union, Any
from pathlib import Path
from pandas import DataFrame

import pandas as pd
import logging
import json

logger = logging.getLogger(__name__)

from .score import Score, MultiScore


class ScoringModel(ABC):
    saved_argsnames: list[str]=["note"]
    
    def __init__(self, height: int=0, note: str="None", *args, **kwargs):
        self.height = height
        self.note = note

    def __call__(self, 
        entities: Union["Entity", "Entities"], 
        criterion: Optional[str]=None
    ) -> MultiScore:
        """ Assigns a score to an entity, or to multiple entities.
        
        Parameters
        ----------
        entities: Union[Entity, Entities]
            
        Returns
        -------
        out: Score or MultiScore
            If entities: Entity with unidimensional scoring, the output is a Score.
            If entities: Entity with multivariate scoring, then out[criterion_name] is a Score.
            If entities: Entities with unidimensional scoring, then out[entity_name] is a Score.
            If entities: Entities with multivariate scoring, then out[entity_name] is a MultiScore.
        """
        from solidago.state.entities import Entities
        if not isinstance(entities, Entities) and criterion is not None:
            return self.score(entities, criterion)
        entities = self.evaluated_entities(entities) if isinstance(entities, Entities) else [entities]
        keynames = ["entity_name"] if isinstance(entities, Entities) else list()
        criteria = self.criteria() if criterion is None else { criterion }
        keynames += ["criterion"] if criterion is None else list()
        result = MultiScore(keynames)
        all_keynames = ["entity_name", "criterion"]
        to_keys = lambda e, c: tuple(k for kn, k in zip(all_keynames, (e, c)) if kn in keynames)
        for e in entities:
            for c in criteria:
                score = self.score(e, c)
                if not score.isnan():
                    result[to_keys(e, c)] = score
        return result
    
    @abstractmethod
    def score(self, entity: "Entity", criterion: str) -> Score:
        raise NotImplementedError
    
    def criteria(self) -> set[str]:
        return self.parent.criteria()
    
    def evaluated_entities(self, entities: "Entities", criterion: Optional[str]=None) -> "Entities":
        return self.parent.evaluated_entities(entities, criterion)
    
    def is_base(self) -> bool:
        return not hasattr(self, "parent")
    
    def to_direct(self, entities: "Entities") -> "DirectScoring":
        from .direct import DirectScoring
        direct_scoring = DirectScoring()
        for (entity, criterion), score in self(entities):
            if not score.isnan():
                direct_scoring[entity, criterion] = score
        return direct_scoring
        
    def saved_kwargs(self) -> dict:
        kwargs = { name: getattr(self, name) for name in self.saved_argsnames }
        if not self.is_base():
            kwargs["parent"] = (type(self.parent).__name__, self.parent.saved_kwargs())
        return kwargs

    def get_directs(self) -> MultiScore:
        if not self.is_base():
            return self.parent.get_directs()
        MultiScore(["entity_name", "criterion"])
        
    def get_scales(self) -> MultiScore:
        if not self.is_base():
            return self.parent.get_scales()
        return MultiScore(["height", "kind", "criterion"])

    @classmethod
    def load(cls, directory: Union[str, Path], **kwargs) -> "ScoringModel":
        for name in ("directs", "scales"):
            if name not in kwargs:
                continue
            try:
                filename = f"{directory}/{kwargs[name]['name']}"
                init_data = pd.read_csv(filename, keep_default_na=False)
            except (pd.errors.EmptyDataError, ValueError):
                init_data = None
            kwargs[name] = MultiScore(kwargs[name]["keynames"], init_data)
        return cls(**kwargs)

    def save(self, directory: Optional[str]=None, json_dump: bool=False) -> tuple[str, dict]:
        """ save must be given a filename_root (typically without extension),
        as multiple csv files may be saved, with a name derived from the filename_root
        (in addition to the json description) """
        for table_name in ("directs", "scales"):
            table = getattr(self, f"get_{table_name}")()
            if table:
                table.save(directory, f"{table_name}.csv")
        return self.save_instructions(directory, json_dump)

    def save_instructions(self, directory: Optional[str]=None, json_dump: bool=False) -> tuple[str, dict]:
        kwargs = self.saved_kwargs()
        for table_name in ("directs", "scales"):
            table = getattr(self, f"get_{table_name}")()
            if table:
                kwargs[table_name] = { "name": f"{table_name}.csv", "keynames": table.keynames }
        if directory is not None and json_dump:
            with open(Path(directory) / "model.json", "w") as f:
                json.dump([type(self).__name__, kwargs], f, indent=4)
        return type(self).__name__, kwargs

    def model_cls_height(model_cls) -> int:
        height, cls = 0, model_cls
        while True:
            if "parent" not in cls[1]:
                return height
            cls = cls[1]["parent"]
            height += 1
            
    def is_cls(self, cls: tuple[str, dict]) -> bool:
        if type(self).__name__ != cls[0]:
            return False
        if any({ getattr(self, key) != value for key, value in cls[1].items() if key != "parent" }):
            return False
        return self.is_base() or self.parent.is_cls(cls[1]["parent"])
    
    def base_model(self) -> "BaseModel":
        return self if self.is_base() else self.parent.base_model()

    def __str__(self) -> str:
        return type(self).__name__
    
    def __repr__(self) -> str:
        types, parent = list(), self
        while True:
            types.append(type(parent).__name__)
            if parent.is_base():
                break
            parent = parent.parent
        r = " > ".join(types)
        tables = self.get_directs(), self.get_scales()
        for name, table in zip(("Directs", "Scales"), tables):
            if table:
                r += f"\n\n{name}\n{repr(table)}"
        return r


class BaseModel(ScoringModel):
    def __init__(self, note: str="None", *args, **kwargs):
        super().__init__(height=0, note=note, *args, **kwargs)

    @abstractmethod
    def score(self, entity: "Entity", criterion: str) -> Score:
        raise NotImplementedError
    
    @abstractmethod
    def criteria(self) -> set[str]:
        raise NotImplementedError
    
    @abstractmethod
    def evaluated_entities(self, entities: "Entities", criterion: Optional[str]=None) -> "Entities":
        raise NotImplementedError


class DerivedModel(ScoringModel):
    def __init__(self, parent: Union[ScoringModel, list, tuple], note: str="None", *args, **kwargs):
        if isinstance(parent, ScoringModel):
            self.parent = parent
        elif isinstance(parent, (list, tuple)):
            assert len(parent) == 2 and isinstance(parent[0], str) and isinstance(parent[1], dict)
            parent_cls, parent_kwargs = parent
            import solidago.state.models as models
            self.parent = getattr(models, parent_cls)(*args, **(kwargs | parent_kwargs))
        else:
            raise ValueError(f"{parent} has unhandled type {type(parent)}")
        super().__init__(self.parent.height + 1, note, *args, **kwargs)
