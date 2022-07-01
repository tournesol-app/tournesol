from __future__ import annotations

from tournesol.suggestions.suggested_user import SuggestedUser
from tournesol.suggestions.suggested_video import SuggestedVideo


class SuggestedUserVideo(SuggestedVideo):
    local_user: SuggestedUser

    def __init__(
            self,
            parent: SuggestedVideo,
            local_user: SuggestedUser
    ):
        super().__init__()
        self._graph_sparsity_score = {}
        self.uid = parent.uid
        self.nb_comparison_with = parent.nb_comparison_with
        self.local_user = local_user

    @property
    def score(self):
        return self.local_user.scores.get(self, 0)

    @property
    def score_uncertainty(self):
        return self.local_user.score_uncertainties.get(self, 0)

    def graph_sparsity(self, reference: SuggestedUserVideo):
        return self._graph_sparsity_score.get(reference, 0)
