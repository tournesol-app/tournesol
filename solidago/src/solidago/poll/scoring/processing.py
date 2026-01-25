from abc import abstractmethod
from typing import Any

import numpy as np

from solidago.poll.scoring.score import MultiScore, Score
from solidago.poll.scoring.model import Multipliers, Translations
    
    
class ScoreProcessing:
    def __init__(self, multipliers: Multipliers, translations: Translations, note: str | None = None):
        assert isinstance(multipliers, Multipliers) and multipliers.keynames == ("criterion",), multipliers
        assert isinstance(translations, Translations) and translations.keynames == ("criterion",), translations
        self.multipliers, self.translations = multipliers, translations
        self.note = note

    @abstractmethod
    def __call__(self, criteria: str | set | slice, scores: Score | MultiScore) -> Score | MultiScore:
        """ Defines how to score entities on criteria using model """

    @abstractmethod
    def matches_composition(self, other: "ScoreProcessing") -> bool:
        """ Used in UserModels to determine if a scoring model matches the default one """


class Scale(ScoreProcessing):
    def __init__(self, multipliers: Multipliers, translations: Translations, note: str | None = None):
        super().__init__(multipliers, translations, note)

    def __call__(self, criteria: str | set | slice, scores: Score | MultiScore) -> Score | MultiScore:
        result = scores * self.multipliers[criteria] + self.translations[criteria]
        if len(result.keynames) == 2:
            result = result.reorder("entity_name", "criterion")
        return result

    def matches_composition(self, other: "ScoreProcessing") -> bool:
        return isinstance(other, Scale)


class Squash(ScoreProcessing):
    def __init__(self, multipliers: Multipliers, translations: Translations, max: float, note: str | None = None):
        super().__init__(multipliers, translations, note)
        assert max > 0, max
        self.max = max

    def __call__(self, criteria: str | set | slice, scores: Score | MultiScore) -> Score | MultiScore:
        """ criteria is not used """
        if isinstance(scores, Score):
            return self.squash_score(scores)
        assert isinstance(scores, MultiScore), scores 
        squashed_scores = MultiScore(scores.keynames)
        for keys, score in scores:
            squashed_scores[*keys] = self.squash_score(score)
        return squashed_scores
    
    def matches_composition(self, other: "ScoreProcessing") -> bool:
        return isinstance(other, Squash) and self.max == other.max
    
    def squash_float(self, x: float) -> float:
        return self.max * x / np.sqrt(1 + x**2)
    
    def squash_score(self, score: Score) -> Score:
        assert isinstance(score, Score), score
        value = self.squash_float(score.value)
        extremes = [self.squash_float(score.max), self.squash_float(score.min)]
        return Score(value, value - min(extremes), max(extremes) - value)