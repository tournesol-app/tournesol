from datetime import timedelta

from solidago.primitives.decay import Decay
from solidago.poll import *
from .volumes import VolumeBiasing


class LikesVolumes(VolumeBiasing):
    default_likes: dict[str, tuple[float, int]] = dict(
        like = (1., timedelta(weeks=52*3).seconds), 
        dislike = (-1., timedelta(weeks=52*3).seconds),
    )

    def __init__(self,
        likes: dict[str, tuple[float, int]] | None = None, 
        decay: Decay | tuple[str, dict] | None = None,
    ):
        """ likes must detail for each kind of social interaction, 
        which weight and lifetime are associated to the interaction """
        self.likes = self.default_likes if likes is None else likes
        import solidago, solidago.primitives.decay as d
        self.decay = solidago.load(decay, d, Decay, d.NoDecay())

    def __call__(self, poll: Poll, receiver: User, time: float, councillors: Users) -> Users:
        kwargs = dict(by=receiver.name, to=councillors.names(), kind=self.default_likes)
        for l in poll.socials.filters(**kwargs):
            bonus, lifetime = self.likes[l["kind"]]
            weight, age = l["weight"], time - l["date"]
            councillors[l["to"], "volume"] += bonus * weight * self.decay(age, lifetime)
        return councillors