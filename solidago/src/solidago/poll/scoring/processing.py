from abc import abstractmethod
from copy import deepcopy
from numpy.typing import NDArray

import numpy as np

from solidago.poll.scoring.score import Scores
from solidago.poll.scoring.model import Multipliers, Translations
    
    
class ScoreProcessing:
    def __init__(self, multipliers: Multipliers, translations: Translations, note: str | None = None):
        assert isinstance(multipliers, Multipliers), (multipliers, type(multipliers))
        assert multipliers.keynames == {"criterion"}, multipliers.keynames
        assert isinstance(translations, Translations), (translations, type(multipliers))
        assert translations.keynames == {"criterion"}, translations.keynames
        self.multipliers, self.translations = multipliers, translations
        self.note = note

    @abstractmethod
    def __call__(self, criteria: set[str], scores: Scores) -> Scores:
        """ Defines how to score entities on criteria using model """

    @abstractmethod
    def matches_composition(self, other: "ScoreProcessing") -> bool:
        """ Used in UserModels to determine if a scoring model matches the default one """

    def __repr__(self) -> str:
        r = f"{type(self).__name__}{f' ({self.note})' if self.note else ''}\n\n"
        for table in (self.multipliers, self.translations):
            if table:
                r += repr(table) + "\n\n"
        return r



class ScaleProcessing(ScoreProcessing):
    def __init__(self, multipliers: Multipliers, translations: Translations, note: str | None = None):
        super().__init__(multipliers, translations, note)

    def __call__(self, criteria: set[str], scores: Scores) -> Scores:
        multipliers = self.multipliers.filters(criterion=list(criteria))
        translations = self.translations.filters(criterion=list(criteria))
        results = scores * multipliers + translations
        assert isinstance(results, Scores)
        return results

    def matches_composition(self, other: "ScoreProcessing") -> bool:
        return isinstance(other, ScaleProcessing)


class SquashProcessing(ScoreProcessing):
    def __init__(self, multipliers: Multipliers, translations: Translations, max: float, note: str | None = None):
        super().__init__(multipliers, translations, note)
        assert max > 0, max
        self.max = max

    def __call__(self, criteria: set[str], scores: Scores) -> Scores:
        """ criteria is not used """
        assert isinstance(scores, Scores), scores 
        squashed_scores = deepcopy(scores)
        value, min, max = self.squash(scores.value), self.squash(scores.min), self.squash(scores.max)
        left_unc, right_unc = value - min, max - value
        squashed_scores.set_columns(value=value, left_unc=left_unc, right_unc=right_unc)
        return squashed_scores
    
    def matches_composition(self, other: "ScoreProcessing") -> bool:
        return isinstance(other, SquashProcessing) and self.max == other.max
    
    def squash(self, x: NDArray[np.float64]) -> NDArray[np.float64]:
        return self.max * x / np.sqrt(1 + x**2)