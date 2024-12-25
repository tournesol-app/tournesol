from abc import ABC, abstractmethod
from typing import Optional, Union
from pathlib import Path

from .assessments import AssessmentsDictionary
from .comparisons import ComparisonsDictionary
        

class Judgments:
    def __init__(self,
        assessments: AssessmentsDictionary=AssessmentsDictionary(),
        comparisons: ComparisonsDictionary=ComparisonsDictionary(),
    ):
        self.assessments = assessments
        self.comparisons = comparisons

    @classmethod
    def load(cls, d: dict[str, tuple[str, Union[str, tuple, dict]]]) -> "Judgments":
        import solidago.state.judgments as judgments
        return cls(**{ key: getattr(judgments, d[key][0]).load(d[key][1]) for key in d })

    def save(self, directory: Union[str, Path]) -> tuple[str, dict[str, str]]:
        return type(self).__name__, {
            key: getattr(self, key).save(directory)
            for key in ("assessments", "comparisons")
        }
