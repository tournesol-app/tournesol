from __future__ import annotations

from functools import total_ordering
from typing import Optional

from tournesol.models import Entity


@total_ordering
class SuggestedVideo:
    uid = ""
    video1_score: float = 0
    video2_score: dict[SuggestedVideo, float] = {}
    beta: dict[SuggestedVideo, float] = {}
    nb_comparison_with: dict[str, int] = {}
    global_video_score_uncertainty: float
    global_video_score: float
    NEW_NODE_CONNECTION_SCORE = 0.5

    user_pref: int = 0

    video_reference: list[SuggestedVideo]

    def __init__(
            self,
            video_reference: Optional[list[SuggestedVideo]],
            from_entity: Optional[Entity] = None
    ):
        self.video_reference = video_reference
        if from_entity is not None:
            self.uid = from_entity.uid

    def __eq__(self, __o: SuggestedVideo) -> bool:
        return __o.uid == self.uid

    def __le__(self, other: SuggestedVideo):
        if len(self.video_reference) == 0:
            return self.video1_score <= other.video1_score
        else:
            #  self.video2_score.get(self.video_reference, self.)
            score_self = self.score_suggestibility + self.graph_sparsity
            score_other = other.score_suggestibility + other.graph_sparsity
            return score_self <= score_other

    def __repr__(self) -> str:
        return (
                "Video "
                + self.uid
        )

    def __hash__(self):
        return self.uid.__hash__()

    @property
    def score_suggestibility(self):
        return self.score_uncertainty + self.video_reference[0].score_uncertainty / (
                    self.score + self.video_reference[0].score + 1)

    @property
    def score(self):
        return self.global_video_score

    @property
    def score_uncertainty(self):
        return self.global_video_score_uncertainty

    @property
    def graph_sparsity(self):
        return self.NEW_NODE_CONNECTION_SCORE

    @property
    def comparison_nb(self):
        return sum(self.nb_comparison_with.values())
