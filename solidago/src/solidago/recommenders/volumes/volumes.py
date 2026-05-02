from abc import abstractmethod
from solidago.poll import *


class BaseVolumes:
    @abstractmethod
    def __call__(self, poll: Poll, receiver: User, time: float) -> Users:
        raise NotImplemented


class VolumeBiasing:
    @abstractmethod
    def __call__(self, poll: Poll, receiver: User, time: float, councillors: Users) -> Users:
        raise NotImplemented


class Volumes:
    def __init__(self,
        base: BaseVolumes | tuple[str, dict] | None = None,
        biases: list[VolumeBiasing | tuple[str, dict]] | None = None,
    ):
        import solidago, solidago.recommenders.volumes as v
        self.base = solidago.load(base, v, BaseVolumes, v.Follows())
        self.biases = [solidago.load(b, v, VolumeBiasing) for b in biases or list()]
        
    def __call__(self, poll: Poll, receiver: User, time: float) -> Users:
        councillors = self.base(poll, receiver, time)
        for bias in self.biases:
            councillors = bias(poll, receiver, time, councillors)
        return councillors