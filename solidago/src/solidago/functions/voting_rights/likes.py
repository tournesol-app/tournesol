import numpy as np

from solidago.functions.poll_function import PollFunction
from solidago.primitives.decay import Decay
from solidago.poll import *
from solidago.primitives.time import Date, DateInput, Duration


class LikesVolumes(PollFunction):
    default_likes: dict[str, tuple[float, float]] = dict(
        like = (1., Duration(weeks=52*3).seconds), 
        dislike = (-1., Duration(weeks=52*3).seconds),
    )

    def __init__(self,
        likes: dict[str, tuple[float, int]] | None = None, 
        decay: Decay | tuple[str, dict] | None = None,
        receiver: User | None = None,
        date: DateInput | None = None,
    ):
        """ likes must detail for each kind of social interaction, 
        which weight and lifetime are associated to the interaction """
        self.likes = self.default_likes if likes is None else likes
        import solidago, solidago.primitives.decay as d
        self.decay = solidago.load(decay, d, Decay, d.NoDecay())
        self.receiver = receiver
        self.date = None if date is None else Date(date)

    def fn(self, users: Users, socials: Socials) -> Users:
        if self.receiver is None:
            self.log_warning("Mentions without receiver. Identity used instead.")
            return users
        
        date = self.date or Date.now()
        users = users.assign(like_volume=0)
        likes = socials.filters(by=self.receiver.name, to=users.names(), kind=self.default_likes)
        bonuses = np.array([b for b, _ in likes("kind")])
        lifetimes = np.array([lt for _, lt in likes("kind")])
        ages = np.array([(date - Date(d)).seconds] for d in likes("date"))
        weights = likes("weight")
        deltas = bonuses * weights * self.decay(ages, lifetimes)
        for l, delta in zip(likes, deltas):
            users[l["to"], "like_volume"] += delta
        return users