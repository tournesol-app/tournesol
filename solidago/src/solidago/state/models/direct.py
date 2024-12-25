from typing import Optional, Union
from pathlib import Path
from pandas import DataFrame, Series

from .base import Score, ScoringModel, BaseModel


class DirectScoring(BaseModel):
    def __init__(self, d: Optional[dict[str, dict[str, Score]]]=None):
        """ dct[str(entity)][str(criterion)] should yield a Score """
        super().__init__()
        self._dict = dict() if d is None else d
        self._criteria_ids = set()
        for entity_id in self._dict:
            self._criteria_ids |= set(self._dict[entity_id].keys())
    
    def criteria_ids(self) -> set[str]:
        return self._criteria_ids
    
    def score(self, entity: Union[str, "Entity"], criterion: Union[str, "Criterion"]) -> Score:
        if str(entity) in self._dict and str(criterion) in self._dict[str(entity)]:
            return self._dict[str(entity)][str(criterion)]
        return Score()

    @classmethod
    def load(cls, d: dict, direct_scores: DataFrame, scalings: dict, depth: int=0) -> "DirectScoring":
        """ The parameters d, scalings, depth are not used by the method """
        model = cls()
        left, right = ("left_unc", "right_unc") if "left_unc" in direct_scores.columns else ("uncertainty", "uncertainty")
        for _, r in direct_scores.iterrows():
            model[r["entity_id"], r["criterion_id"]] = Score(r["score"], r[left], r[right])
        return model
    
    def save(self, filename: Union[Path, str], depth: int=0, save_scores: bool=False) -> tuple[str, str]:
        if not save_scores:
            return [self.__class__.__name__, dict()]            
        filename = Path(filename)
        if filename.is_dir():
            filename /= "direct_scores.csv"
        self.to_df(depth).to_csv(filename, index=False)
        return [self.__class__.__name__, str(filename)]
    
    def __setitem__(self, entity_criterion: tuple["Entity", "Criterion"], score: Score) -> None:
        entity, criterion = entity_criterion
        self._criteria_ids.add(str(criterion))
        if not str(entity) in self._dict:
            self._dict[str(entity)] = dict()
        self._dict[str(entity)][str(criterion)] = score

    def scored_entity_ids(self, 
        entities: Optional["Entities"]=None, 
        criterion: Optional[Union["Criterion", "Criteria"]]=None
    ) -> set[str]:
        from solidago.state import Criteria
        if criterion is None:
            all_scored_entities = set(self._dict.keys())
        elif isinstance(criterion, Criteria):
            all_scored_entities = {
                entities.get(entity_id) for entity_id in self._dict 
                if any(set(criterion["criterion_id"]) & set(self._dict[entity_id]))
            }
        else:
            all_scored_entities = {
                entities.get(entity_id) for entity_id in self._dict 
                if str(criterion) in self._dict[e] 
            }
        from solidago.state.entities import Entities
        if entities is None:
            return all_scored_entities
        return set(entities) & all_scored_entities

    def to_df(self, depth: int=0) -> DataFrame:
        rows = list()
        for entity_id in self._dict:
            for criterion_id in self._dict[entity_id]:
                score = self(entity_id, criterion_id)
                rows.append([entity_id, criterion_id, score.value, score.left, score.right, depth])
        return DataFrame(rows, columns=["entity_id", "criterion_id", "score", "left_unc", "right_unc", "depth"])

    def to_dict(self, data=False) -> tuple[str, dict]:
        return [self.__class__.__name__, dict() if not data else { 
            entity_id: {
                criterion_id: self.score(entity_id, criterion_id).to_triplet() 
                for criterion_id in self._dict[entity_id]
            }
            for entity_id in self._dict
        }]
    
    @classmethod
    def from_dict(cls, d: dict) -> "DirectScoring":
        """ This assumes that all the model scores are stored in d """
        model = DirectScoring()
        for entity_id, entity_dict in d.items():
            for criterion_id, score_triplet in entity_dict.items():
                model[entity_id, criterion_id] = Score(*score_triplet)
        return model

    def __repr__(self) -> str:
        return repr(self.to_df())
        
