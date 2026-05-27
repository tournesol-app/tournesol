import numpy as np

from solidago.functions.poll_function import PollFunction
from solidago.primitives.decay import Decay
from solidago.poll import *
from solidago.primitives.time import Date, DateInput, Duration


class LikesVolumes(PollFunction):
    default_likes: dict[str, tuple[float, float]] = dict(
        like = (1., Duration(weeks=52*3).total_seconds), 
        dislike = (-1., Duration(weeks=52*3).total_seconds),
    )

    def __init__(self,
        likes: dict[str, tuple[float, int]] | None = None, 
        decay: Decay | tuple[str, dict] | None = None,
        username: str | None = None,
        date: DateInput | None = None,
    ):
        """ likes must detail for each kind of social interaction, 
        which weight and lifetime are associated to the interaction """
        self.likes = self.default_likes if likes is None else likes
        import solidago, solidago.primitives.decay as d
        self.decay = solidago.load(decay, d, Decay, d.NoDecay())
        self.username = username
        self.date = None if date is None else Date(date)

    def fn(self, users: Users, socials: Socials, voting_rights: VotingRights) -> VotingRights:
        voting_rights = voting_rights.add_columns(like_volume=0)
        if self.username is None:
            self.log_warning("Mentions without receiver. Setting like volumes to zero.")
            return voting_rights
        
        likes = socials.filters(by=self.username, to=users.names(), kind=self.default_likes)
        bonuses = np.array([self.likes[k][0] for k in likes("kind")])
        lifetimes = np.array([self.likes[k][1] for k in likes("kind")])
        t = (self.date or Date.now()).timestamp()
        ages = t - likes("timestamp", t)
        deltas = bonuses * likes("weight", 1.) * self.decay(ages, lifetimes)
        for like, delta in zip(likes, deltas):
            voting_right = voting_rights.get(username=like["to"])
            like_volume = voting_right.get("like_volume", 0)
            voting_rights.set(voting_right, like_volume=like_volume+delta)
        return voting_rights