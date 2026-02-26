from abc import abstractmethod
from typing import Iterable
import numpy as np

from solidago.poll.poll_tables import *
from .score import Score, Scores
from .model import Parameters, CategoryScores


class BaseScoring:
    def __init__(self, directs: Scores, categories: CategoryScores, parameters: Parameters, note: str | None = None):
        assert isinstance(directs, Scores), directs
        assert isinstance(categories, CategoryScores), categories
        assert isinstance(parameters, Parameters), parameters
        self.directs = directs
        self.categories = categories
        self.parameters = parameters
        self.note = note

    @abstractmethod
    def __call__(self, entities: Entity | Entities, criteria: str | Iterable[str] | None) -> Score | Scores:
        """ Defines how to score entities on criteria """

    @abstractmethod
    def matches_composition(self, other: "BaseScoring") -> bool:
        """ Used in UserModels to test composition matching """

class Linear(BaseScoring):
    def __call__(self, entities: Entity | Entities, criteria: str | Iterable[str] | None) -> Score | Scores:
        """ Defines how to score entities on criteria """
        if self.directs and not self.categories and not self.parameters:
            return self.direct_scoring(entities, criteria)
        scores = Scores(keynames=["entity_name", "criterion"], default_score=(0., 0., 0.))
        if self.directs:
            scores += self.direct_scoring(entities, criteria)
        if self.categories:
            scores += self.categories_scoring(entities, criteria)
        if self.parameters:
            scores += self.linear_scoring(entities, criteria)
        assert isinstance(scores, Scores)
        if isinstance(entities, Entity) and isinstance(criteria, str):
            return scores.get("unique")
        if isinstance(entities, Entity):
            scores = scores.filters(entity_name=entities.name)
        if isinstance(criteria, str):
            scores = scores.filters(criterion=criteria)
        return scores
    
    def direct_scoring(self, entities: Entity | Entities, criteria: str | Iterable[str] | None) -> Scores:
        keys = dict(entity_name=list(entities.names()) if isinstance(entities, Entities) else entities.name)
        if criteria is not None:
            keys["criterion"] = criteria if isinstance(criteria, str) else list(criteria)
        return Scores(
            self.directs.df, 
            keynames=["entity_name", "criterion"], 
            default_score=self.directs.default_score
        ).filters(**keys)
    
    def categories_scoring(self, entities: Entity | Entities, criteria: str | Iterable[str] | None) -> Scores:
        scores = Scores(keynames=["entity_name", "criterion"], default_score=(0., 0., 0.))
        categories = self.categories.keys("category")
        if criteria is not None:
            criteria = {str(c) for c in self.categories.keys("criterion")}
        assert criteria is not None
        for category in categories:
            for entity in (entities if isinstance(entities, Entities) else [entities]):
                group = entity[str(category)]
                for criterion in ([criteria] if isinstance(criteria, str) else criteria):
                    score = self.categories.get("unique", category=category, group=group, criterion=criterion)
                    scores.set(score, entity_name=entity.name, criterion=criterion)
        return scores

    def linear_scoring(self, entities: Entity | Entities, criteria: str | Iterable[str] | None) -> Scores:
        scores = Scores(keynames=["entity_name", "criterion"], default_score=(0., 0., 0.))
        if criteria is not None:
            criteria = {str(c) for c in self.categories.keys("criterion")}
        assert criteria is not None
        for entity in (entities if isinstance(entities, Entities) else [entities]):
            entity_vector = entity.vector
            for criterion in ([criteria] if isinstance(criteria, str) else criteria):
                linear_value = self.parameters.values(criteria) @ entity_vector
                mins, maxs = self.parameters.minima(criterion), self.parameters.maxima(criterion)
                minimizer = np.where(entity_vector > 0, maxs, mins)
                min_linear_value = minimizer @ entity_vector
                maximizer = np.where(entity_vector < 0, maxs, mins)
                max_linear_value = maximizer @ entity_vector
                assert min_linear_value <= linear_value and linear_value <= max_linear_value
                score = Score((linear_value, linear_value - min_linear_value, max_linear_value - linear_value))
                scores.set(score, entity_name=entity.name, criterion=criterion)
        return scores

    def matches_composition(self, other: "BaseScoring") -> bool:
        return type(other) == Linear

    def __repr__(self) -> str:
        r = f"{type(self).__name__}{f' ({self.note})' if self.note else ''}\n\n"
        for table in (self.directs, self.categories, self.parameters):
            if table:
                r += repr(table) + "\n\n"
        return r
