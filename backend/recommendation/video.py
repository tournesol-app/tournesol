from __future__ import annotations

from functools import total_ordering


@total_ordering
class Video:
    uid = ""
    v1_score: float = 0
    v2_score: dict[Video, float] = {}
    beta: dict[Video, float] = {}
    estimated_information_gains = []
    nb_comparison_with: dict[str, int] = {}

    comparison_nb: int = 0
    user_pref: int = 0

    video_reference: Video

    def __init__(self, video_reference: Video):
        self.video_reference = video_reference

    def __eq__(self, __o: Video) -> bool:
        return __o.uid == self.uid

    def __gt__(self, obj):
        if self.video_reference.uid == "":
            return self.v1_score > obj.v1_score
        else:
            return self.v2_score[self.video_reference] > obj.v2_scoreself.video_reference

    def __le__(self, other):
        if self.video_reference.uid == "":
            return self.v1_score <= other.v1_score
        else:
            return self.v2_score[self.video_reference] <= other.v2_score[self.video_reference]

    def __repr__(self) -> str:
        return "Video " + self.uid + \
               " with score v1 " + str(self.v1_score) + \
               " and scores v2 " + str(self.v2_score)
