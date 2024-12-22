from typing import Optional, Union
from pathlib import Path

import pandas as pd
import numpy as np

from .base import Score, ScoringModel


class DirectScoring(ScoringModel):
    def __init__(self, dct: dict[str, dict[str, Score]]=dict()):
        """ dct[entity.id][criterion] should yield a Score """
        super().__init__()
        self._dict = dct
        self.iterator = None
    
    def score(self, entity: "Entity", criterion: str) -> Score:
        if entity.id in self._dict and criterion in self._dict[entity.id]:
            return self._dict[entity.id][criterion]
        return Score()

    @classmethod
    def load(cls, d: Optional[dict], model: "DirectScoring", scalings: Optional[dict]=None, depth: int=0):
        """ The parameters d, scalings, depth are not used by the method """
        return model
    
    def save(self, directory: Union[Path, str], filename: str="scores", depth: int=0) -> Union[str, list, dict]:
        df = pd.DataFrame(columns=["entity_id", "criterion", "score", "left_unc", "right_unc"])
        for entity in self._dict:
            for criterion in self._dict[entity]:
                score = self(entity, criterion)
                df.iloc[-1] = [entity.id, criterion, score.value, score.left, score.right]
        filename = filename if depth == 0 else f"{filename}_{depth}"
        df.to_csv(Path(directory) / f"{filename}.csv")
        return [self.__class__.__name__, str(filename)]
    
    def __setitem__(self, entity_criterion: tuple[Union["Entity", str], str], score: Score):
        entity, criterion = entity_criterion
        entity_id = entity if isinstance(entity, str) else entity.id
        if not entity_id in self._dict:
            self._dict[entity_id] = dict()
        self._dict[entity_id][criterion] = score

    def scored_entities(self, entities: "Entities", criterion: Optional[str]=None) -> "Entities":
        all_scored_entities = list(self._dict.keys()) if criterion is None else [
            entities.get(e) for e in self._dict if criterion in self._dict[e]
        ]
        if entities is None:
            return Entities(all_scored_entities)
        from solidago.state.entities import Entities
        return Entities(entities[entities.id.isin(all_scored_entities)])

    def to_dict(self, data=False):
        return [self.__class__.__name__, dict() if not data else { 
            entity.id: {
                criterion: self.score(entity, criterion).to_dict() 
                for criterion in self._dict[entity]
            }
            for entity in self._dict
        }]
    
    @classmethod
    def from_dict(cls, d: dict):
        """ This assumes that all the model scores are stored in d """
        model = DirectScoring()
        for entity, entity_dict in d.items():
            for criterion, score_triplet in entity_dict.items():
                model[entity, criterion] = Score(*score_triplet)
        return model

        
