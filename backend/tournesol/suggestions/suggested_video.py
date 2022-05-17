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
    estimated_information_gains = []
    nb_comparison_with: dict[str, int] = {}

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
            return (
                    self.video2_score[self.video_reference]
                    <= other.video2_score[self.video_reference]
            )

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
