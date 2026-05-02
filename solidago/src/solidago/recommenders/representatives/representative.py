from solidago.primitives.datastructure import Contains
from solidago.poll import *
from .base import BaseBallotConstructor
from ..bias import BallotBiasing

class Representative:
    def __init__(self, 
        base: BaseBallotConstructor | tuple[str, dict] | None = None,
        biases: list[BallotBiasing | tuple[str, dict]] | None = None,
    ):
        import solidago, solidago.recommenders.representatives as r
        self.base = solidago.load(base, r.base, BaseBallotConstructor, r.base.Direct())
        self.biases = [
            solidago.load(bias, solidago.recommenders.bias, BallotBiasing)
            for bias in biases or list()
        ]
        
    def __call__(self, poll: Poll, councillor: User, receiver: User | None = None) -> Scores:
        entities = poll.entities.filters(authors=Contains(councillor.name))
        ratings = poll.ratings.filters(username=councillor.name)
        ballot = self.base(councillor, entities, ratings)
        for bias in self.biases:
            ballot = bias(poll, ballot)
        return ballot