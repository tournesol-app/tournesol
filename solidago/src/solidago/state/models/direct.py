from typing import Optional, Union
from pathlib import Path
from pandas import DataFrame

from .base import Score, ScoringModel


class DirectScoring(ScoringModel):
    def __init__(self, d: Optional[dict[str, dict[str, Score]]]=None):
        """ dct[entity.id][criterion] should yield a Score """
        super().__init__()
        self._dict = dict() if d is None else d
        self._criteria = set()
        for entity_id in self._dict:
            self._criteria |= set(self._dict[entity_id].keys())
    
    def criteria(self):
        return self._criteria
    
    def score(self, entity: Union[int, str, "Entity"], criterion: str) -> Score:
        entity_id = entity if isinstance(entity, (str, int)) else entity.id
        if entity_id in self._dict and criterion in self._dict[entity_id]:
            return self._dict[entity_id][criterion]
        return Score()

    @classmethod
    def load(cls, d: dict, direct_scores: DataFrame, scalings: dict, depth: int=0):
        """ The parameters d, scalings, depth are not used by the method """
        model = cls()
        left, right = ("left_unc", "right_unc") if "left_unc" in direct_scores.columns else ("uncertainty", "uncertainty")
        for _, r in direct_scores.iterrows():
            model[r["entity_id"], r["criterion"]] = Score(r["score"], r[left], r[right])
        return model
    
    def save(self, filename: Union[Path, str], depth: int=0) -> Union[str, list, dict]:
        filename = Path(filename)
        if filename.is_dir():
            filename /= "direct_scores.csv"
        df = DataFrame(columns=["entity_id", "criterion", "score", "left_unc", "right_unc"])
        for entity_id in self._dict:
            for criterion in self._dict[entity_id]:
                score = self(entity_id, criterion)
                df.iloc[-1] = [entity_id, criterion, score.value, score.left, score.right]
        df.to_csv(filename)
        return [self.__class__.__name__, str(filename)]
    
    def __setitem__(self, entity_criterion: tuple[Union["Entity", str], str], score: Score):
        entity, criterion = entity_criterion
        self._criteria.add(criterion)
        entity_id = entity if isinstance(entity, str) else entity.id
        if not entity_id in self._dict:
            self._dict[entity_id] = dict()
        self._dict[entity_id][criterion] = score

    def scored_entities(self, entities: "Entities", criterion: Optional[str]=None) -> "Entities":
        all_scored_entities = list(self._dict.keys()) if criterion is None else [
            entities.get(e) for e in self._dict if criterion in self._dict[e]
        ]
        from solidago.state.entities import Entities
        if entities is None:
            return Entities(all_scored_entities)
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

        
