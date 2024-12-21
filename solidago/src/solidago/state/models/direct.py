from typing import Optional, Union
from pathlib import Path

import pandas as pd
import numpy as np

from .base import Score, ScoringModel


class DirectScoring(ScoringModel):
    def __init__(self, dct: dict["Entity", dict[str, Score]]=dict()):
        """ dct[entity][criterion] should yield a Score """
        super().__init__()
        self._dict = dct
        self.iterator = None
    
    def score(self, entity: "Entity", criterion: str) -> Score:
        if entity.id in self._dict and criterion in self._dict[entity]:
            return self._dict[entity][criterion]
        return Score()

    @classmethod
    def load(cls, filename: str, entities: "Entities", direct_scores: pd.DataFrame, scalings: pd.DataFrame, depth: int=0):
        model = cls()
        left, right = "left_unc", "right_unc" if "left_unc" in direct_scores.columns else "uncertainty", "uncertainty"
        for _, r in direct_scores.iterrows():
            key = (state.entities.get(r["entity_id"]), r["criterion"])
            model[key] = Score(r["score"], r[left], r[right])
        return model
    
    @classmethod
    def from_dict(cls, d: dict, state: tuple["Entities", pd.DataFrame, pd.DataFrame]):
        model = DirectScoring()
        entities, _, direct_scores = state
        left, right = "left_unc", "right_unc"
        if "left_unc" not in direct_scores.columns:
            assert "uncertainty" in direct_scores.columns
            left, right = "uncertainty", "uncertainty"
        for _, r in direct_scores.iterrows():
            key = (entities.get(r["entity_id"]), r["criterion"])
            model[key] = Score(r["score"], r[left], r[right])
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
    
    def __setitem__(self, entity_criterion: tuple["Entity", str], score: Score):
        self._dict[entity_criterion[0]][entity_criterion[1]] = score

    def scored_entities(self, entities: Optional["Entities"], criterion: Optional[str]=None) -> "Entities":
        all_scored_entities = list(self._dict.keys()) if criterion is None else [
            e for e in self._dict if criterion in self._dict[e]
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
        model = DirectScoring()
        for entity, entity_dict in d.items():
            for criterion, score_triplet in entity_dict.items():
                model[entity, criterion] = Score(*score_triplet)
        return model
