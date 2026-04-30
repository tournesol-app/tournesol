from solidago.poll import *
from .base import BaseBallotConstructor

class Direct(BaseBallotConstructor):
    default_criteria_weights: dict = dict(repost=1, report=-1)

    def __init__(self, councillor: User, criteria_weights: dict | None = None):
        self.councillor = councillor
        self.criteria_weights = criteria_weights or self.default_criteria_weights

    def __call__(self, entities: Entities, ratings: Ratings) -> Scores:
        scores = Scores(keynames=["entity_name"])
        
        for e in entities.filters(author=self.councillor.name):
            scores.append(Score(1), entity_name=e.name, date=e["date"])

        kwargs = dict(username=self.councillor.name, criterion=self.criteria_weights.keys())
        for r in ratings.filters(**kwargs):
            name, date, criterion = r["entity_name"], r["timestamp"], r["criterion"]
            if date > scores.get(entity_name=name)["timestamp"]:
                score = Score(self.criteria_weights[criterion])
                scores.append(score, entity_name=name, date=date)

        return scores