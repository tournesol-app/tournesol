from __future__ import annotations

from functools import total_ordering
from typing import Optional

from tournesol.models import Entity
from tournesol.suggestions.suggested_user import SuggestedUser


@total_ordering
class SuggestedVideo:
    uid = ""
    video1_score: float = 0
    video2_score: dict[SuggestedVideo, float] = {}
    beta: dict[SuggestedVideo, float] = {}
    nb_comparison_with: dict[str, int] = {}
    _global_video_score_uncertainty: float
    _global_video_score: float
    NEW_NODE_CONNECTION_SCORE = 0.5

    comparison_nb: int = 0
    user_pref: int = 0

    video_reference: SuggestedVideo

    def __init__(
            self,
            video_reference: Optional[SuggestedVideo],
            from_entity: Optional[Entity] = None
    ):
        self.video_reference = video_reference
        if from_entity is not None:
            self.uid = from_entity.uid

    def __eq__(self, __o: SuggestedVideo) -> bool:
        return __o.uid == self.uid

    def __gt__(self, other: SuggestedVideo):
        if self.video_reference.uid == "":
            return self.video1_score > other.video1_score
        else:
            return (
                    self.video2_score[self.video_reference]
                    > other.video2_score[self.video_reference]
            )

    def __le__(self, other: SuggestedVideo):
        if self.video_reference.uid == "":
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
                + " with score v1 "
                + str(self.video1_score)
                + " and scores v2 "
                + str(self.video2_score)
        )

    def __hash__(self):
        return self.uid.__hash__()

    @property
    def score_suggestibility(self):
        return self.score_uncertainty + self.video_reference.score_uncertainty / (
                    self.score + self.video_reference.score + 1)

    @property
    def score(self):
        return self._global_video_score

    @property
    def score_uncertainty(self):
        return self._global_video_score_uncertainty

    @property
    def graph_sparsity(self):
        return self.NEW_NODE_CONNECTION_SCORE


class SuggestedUserVideo(SuggestedVideo):
    local_user: SuggestedUser

    def __init__(
            self, video_reference: SuggestedVideo,
            parent: SuggestedVideo,
            local_user: SuggestedUser
    ):
        super().__init__(video_reference)
        self._graph_sparsity_score = 0
        self.uid = parent.uid
        self.nb_comparison_with = parent.nb_comparison_with
        self.local_user = local_user

    @property
    def score(self):
        return self.local_user.scores[self]

    @property
    def score_uncertainty(self):
        return self.local_user.score_uncertainties[self]

    @property
    def graph_sparsity(self):
        return self._graph_sparsity_score
