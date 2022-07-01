from __future__ import annotations

from functools import total_ordering
from typing import Optional


@total_ordering
class SuggestedVideo:
    uid = ""
    video1_score: float = 0
    beta: dict[SuggestedVideo, float] = {}
    nb_comparison_with: dict[str, int] = {}
    global_video_score_uncertainty: float
    global_video_score: float
    suggestibility_normalization: float
    NEW_NODE_CONNECTION_SCORE = 0.5
    NEW_NODE_SCORE_UNCERTAINTY = 1
    NEW_NODE_SCORE = 0

    user_pref: float = 0

    def __init__(
            self,
            from_uid: Optional[str] = None
    ):
        if from_uid is not None:
            self.uid = from_uid
        self.global_video_score = self.NEW_NODE_SCORE
        self.global_video_score_uncertainty = self.NEW_NODE_SCORE_UNCERTAINTY
        self.suggestibility_normalization = 1

    def __eq__(self, __o: SuggestedVideo) -> bool:
        return __o.uid == self.uid

    def __le__(self, other: SuggestedVideo):
        return self.uid <= other.uid

    def __repr__(self) -> str:
        return "Video " + self.uid

    def __hash__(self):
        return self.uid.__hash__()

    def uncertainty_diminution(self, reference: SuggestedVideo):
        return (
            (self.score_uncertainty + reference.score_uncertainty)
            / (abs(self.score - reference.score) + 1)
        )

    def score_computation(self, reference: SuggestedVideo):
        return (self.uncertainty_diminution(reference)
                / self.suggestibility_normalization) + self.graph_sparsity(reference)

    @property
    def score(self):
        return self.global_video_score

    @property
    def score_uncertainty(self):
        return self.global_video_score_uncertainty

    def graph_sparsity(self, reference: SuggestedVideo):
        return self.NEW_NODE_CONNECTION_SCORE

    @property
    def comparison_nb(self):
        return sum(self.nb_comparison_with.values())
