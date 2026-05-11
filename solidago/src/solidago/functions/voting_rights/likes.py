from datetime import timedelta, datetime

import numpy as np

from solidago.functions.poll_function import PollFunction
from solidago.primitives.decay import Decay
from solidago.poll import *


class LikesVolumes(PollFunction):
    default_likes: dict[str, tuple[float, int]] = dict(
        like = (1., timedelta(weeks=52*3).seconds), 
        dislike = (-1., timedelta(weeks=52*3).seconds),
    )

    def __init__(self,
        likes: dict[str, tuple[float, int]] | None = None, 
        decay: Decay | tuple[str, dict] | None = None,
        receiver: User | None = None,
        time: int | None = None,
    ):
        """ likes must detail for each kind of social interaction, 
        which weight and lifetime are associated to the interaction """
        self.likes = self.default_likes if likes is None else likes
        import solidago, solidago.primitives.decay as d
        self.decay = solidago.load(decay, d, Decay, d.NoDecay())
        self.receiver = receiver
        self.time = time

    def fn(self, users: Users, socials: Socials) -> Users:
        if self.receiver is None:
            self.log_warning("Mentions without receiver. Identity used instead.")
            return users
        
        users = users.assign(like_volume=0)
        for l in socials.filters(by=self.receiver.name, to=users.names(), kind=self.default_likes):
            bonus, lifetime = self.likes[l["kind"]]
            weight, age = l["weight"], (self.time or datetime.now().second) - l["date"]
            users[l["to"], "like_volume"] += bonus * weight * self.decay(age, lifetime)
        return users