from abc import abstractmethod

from solidago.poll import Entities


class Sampler:
    @abstractmethod
    def __call__(self, weights: Entities, limit: int) -> Entities:
        raise NotImplemented