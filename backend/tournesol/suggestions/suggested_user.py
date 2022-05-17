from core.models.user import User as UserDB
from tournesol.models import ContributorRatingCriteriaScore, Entity, Poll
from tournesol.suggestions.suggested_video import SuggestedVideo


class SuggestedUser:
    uid: str

    scores: dict[SuggestedVideo, float]
    score_uncertainties: dict[SuggestedVideo, float]

    def __init__(
        self,
        entity_to_video: dict[Entity, SuggestedVideo],
        base_user: UserDB,
        local_criteria: str,
        concerned_poll: Poll,
    ):
        self.uid = base_user.email

        contributor_ratings = (
            ContributorRatingCriteriaScore.objects.filter(
                contributor_rating__user__email=base_user.email
            )
            .filter(contributor_rating__poll__name=concerned_poll.name)
            .filter(criteria=local_criteria)
        )

        self.score_uncertainties = {}
        self.scores = {}
        for rating in contributor_ratings:
            corresponding_video = entity_to_video[rating.contributor_rating.entity]
            self.score_uncertainties[corresponding_video] = rating.uncertainty
            self.scores[corresponding_video] = rating.score

    @property
    def theta(self):
        return self.scores

    @property
    def delta_theta(self):
        return self.score_uncertainties
