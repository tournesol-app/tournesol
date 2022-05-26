from tournesol.suggestions.suggested_user import SuggestedUser
from tournesol.suggestions.suggested_video import SuggestedVideo


class SuggestedUserVideo(SuggestedVideo):
    local_user: SuggestedUser

    def __init__(
            self, video_reference: list[SuggestedVideo],
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
