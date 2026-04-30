from solidago.poll import *
from .base import BaseBallotConstructor
from ..bias import BallotBiasing

class Representative:
    def __init__(self, 
        poll: Poll, 
        councillor: User | str, 
        base: BaseBallotConstructor | tuple[str, dict] | None = None,
        biases: list[BallotBiasing | tuple[str, dict]] | None = None,
    ):
        self.poll = poll
        self.councillor = poll.users[councillor]
        import solidago, solidago.recommenders.representatives as r
        self.base = solidago.load(base, r.base, BaseBallotConstructor, 
            r.base.Direct(self.councillor))
        self.biases = [
            solidago.load(bias, solidago.recommenders.bias, BallotBiasing)
            for bias in biases or list()
        ]
        
    def __call__(self, target_user: User | None = None) -> Scores:
        entities = self.poll.entities.filters(author=self.councillor.name)
        ratings = self.poll.ratings.filters(username=self.councillor.name)
        ballot = self.base(entities, ratings)
        for bias in self.biases:
            ballot = bias(entities, ballot)
        return ballot