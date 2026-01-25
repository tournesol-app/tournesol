from abc import abstractmethod
import itertools
from typing import Callable
import numpy as np
from numpy.typing import NDArray

from solidago.poll.entities.entities import Entities, Entity
from solidago.poll.scoring.score import MultiScore, Score
from solidago.poll.scoring.model import Parameters, CategoryScores


class BaseScoring:
    def __init__(self, directs: MultiScore, categories: CategoryScores, parameters: Parameters, note: str | None = None):
        assert isinstance(directs, MultiScore), directs
        assert directs.keynames == ("entity_name", "criterion"), directs
        assert isinstance(categories, CategoryScores), categories
        assert categories.keynames == ("category", "group", "criterion"), categories
        assert isinstance(parameters, Parameters), parameters
        assert parameters.keynames == ("criterion", "coordinate"), parameters
        self.directs = directs
        self.categories = categories
        self.parameters = parameters
        self.note = note

    @abstractmethod
    def __call__(self, 
        entities: str | Entity | Entities | slice, 
        criteria: str | set | slice,
        keynames: list[str],
    ) -> Score | MultiScore:
        """ Defines how to score entities on criteria """
    
    @abstractmethod
    def score_single(self, entity: str | Entity, criterion: str) -> Score:
        """ Defines how to score a single entity on a single criterion """

    @abstractmethod
    def matches_composition(self, other: "BaseScoring") -> bool:
        """ Used in UserModels to determine if a scoring model matches the default one """


class Direct(BaseScoring):
    def __call__(self, 
        entities: str | Entity | Entities | slice, 
        criteria: str | set | slice,
        keynames: list[str],
    ) -> Score | MultiScore:
        scores = self.directs[entities, criteria]
        return scores if isinstance(scores, Score) else scores.reorder(*keynames)
    
    def score_single(self, entity: str | Entity, criterion: str) -> Score:
        return self.directs[entity, criterion]
    
    def matches_composition(self, other: "BaseScoring") -> bool:
        return isinstance(other, Direct)


class IterateEntitiesCriterion(BaseScoring):
    def __call__(self, entities: Entity | Entities, criteria: str | set, keynames: list[str]) -> Score | MultiScore:
        assert isinstance(entities, (Entity, Entities))
        assert isinstance(criteria, (str, set))
        if isinstance(entities, Entity) and isinstance(criteria, str):
            return self.score_single(entities, criteria)
        scores = MultiScore(keynames)
        entities = Entities([entities]) if isinstance(entities, Entities) else entities
        criteria = {criteria} if isinstance(criteria, str) else criteria
        to_keys = self.to_keys(keynames)
        for entity, criterion in itertools.product(entities, criteria):
            scores[*to_keys(entity, criterion)] = self.score_single(entity, criterion)
        return scores
    
    def to_keys(keynames: list[str]) -> Callable[[Entity, str], tuple]:
        if keynames == ["entity_name"]:
            return lambda entity, criterion: (entity.name,)
        if keynames == ["criterion"]:
            return lambda entity, criterion: (criterion,)
        if keynames == ["entity_name", "criterion"]:
            return lambda entity, criterion: (entity.name, criterion)
        if keynames == ["criterion", "entity_name"]:
            return lambda entity, criterion: (criterion, entity.name)
        raise ValueError(keynames)


class DirectAndMeta(IterateEntitiesCriterion):
    def score_single(self, entity: Entity, criterion: str) -> Score:
        score = self.directs[entity, criterion]
        for category in self.categories.list:
            assert hasattr(entity, category), f"Entity must have a category {category}"
            score += self.categories[category, getattr(entity, category), criterion]
        return score

    def matches_composition(self, other: "BaseScoring") -> bool:
        return isinstance(other, DirectAndMeta)


class Linear(BaseScoring):
    def score_single(self, entity: Entity, criterion: str) -> Score:
        assert self.parameters.n_coordinates == entity.vector.shape
        score = self.directs[entity, criterion]
        for category in self.categories.list:
            assert hasattr(entity, category), f"Entity must have a category {category}"
            score += self.categories[category, getattr(entity, category), criterion]
        linear_value = self.parameters.values(criterion) @ entity.vector
        mins, maxs = self.parameters.minima(criterion), self.parameters.maxima(criterion)
        minimizer = np.where(entity.vector > 0, maxs, mins)
        min_linear_value = minimizer @ entity.vector
        maximizer = np.where(entity.vector < 0, maxs, mins)
        max_linear_value = maximizer @ entity.vector
        assert min_linear_value <= linear_value and linear_value <= max_linear_value
        return score + Score(linear_value, linear_value - min_linear_value, max_linear_value - linear_value)

    def matches_composition(self, other: "BaseScoring") -> bool:
        return isinstance(other, Linear)