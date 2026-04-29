from abc import abstractmethod
from solidago.poll import Users, Entities, Scores


class Aggregator:
    @abstractmethod
    def __call__(self, users: Users, entities: Entities, ballots: Scores) -> Entities:
        raise NotImplemented