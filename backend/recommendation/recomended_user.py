from recommendation.video import Video


class User:
    uid: str
    mean_score: float

    scaling_accuracy: float
    translation_accuracy: float

    scores: dict[Video, float]
    score_uncertainties: dict[Video, float]

    @property
    def theta(self):
        return self.scores

    @property
    def delta_theta(self):
        return self.score_uncertainties
