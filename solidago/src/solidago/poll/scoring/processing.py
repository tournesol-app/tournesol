from abc import abstractmethod
from copy import deepcopy
from typing import Any, Iterable

import numpy as np

from solidago.poll.scoring.score import Scores, Score
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
    def __call__(self, criteria: str | Iterable[str] | None, scores: Score | Scores) -> Score | Scores:
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



class Scale(ScoreProcessing):
    def __init__(self, multipliers: Multipliers, translations: Translations, note: str | None = None):
        super().__init__(multipliers, translations, note)

    def __call__(self, criteria: str | Iterable[str] | None, scores: Score | Scores) -> Score | Scores:
        if criteria is None:
            criteria = str(scores["criterion"]) if isinstance(scores, Score) else {str(c) for c in scores.keys("criterion")}
        criteria = criteria if isinstance(criteria, str) else list(criteria)
        multipliers = self.multipliers.filters(criterion=criteria) # type: ignore
        translations = self.translations.filters(criterion=criteria) # type: ignore
        return scores * multipliers + translations

    def matches_composition(self, other: "ScoreProcessing") -> bool:
        return isinstance(other, Scale)


class Squash(ScoreProcessing):
    def __init__(self, multipliers: Multipliers, translations: Translations, max: float, note: str | None = None):
        super().__init__(multipliers, translations, note)
        assert max > 0, max
        self.max = max

    def __call__(self, criteria: str | Iterable[str] | None, scores: Score | Scores) -> Score | Scores:
        """ criteria is not used """
        if isinstance(scores, Score):
            return self.squash_score(scores)
        assert isinstance(scores, Scores), scores 
        squashed_scores = deepcopy(scores)
        value = scores.value * self.max / np.sqrt(1 + scores.value**2)
        min = scores.min * self.max / np.sqrt(1 + scores.min**2)
        max = scores.max * self.max / np.sqrt(1 + scores.max**2)
        left_unc, right_unc = value - min, max - value
        squashed_scores.set_columns(value=value, left_unc=left_unc, right_unc=right_unc)
        return squashed_scores
    
    def matches_composition(self, other: "ScoreProcessing") -> bool:
        return isinstance(other, Squash) and self.max == other.max
    
    def squash_float(self, x: float) -> float:
        return self.max * x / np.sqrt(1 + x**2)
    
    def squash_score(self, score: Score) -> Score:
        assert isinstance(score, Score), score
        value = self.squash_float(score.value)
        extremes = [self.squash_float(score.max), self.squash_float(score.min)]
        return Score((value, value - min(extremes), max(extremes) - value))
