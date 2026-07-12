import numpy as np

from solidago.functions.poll_function import PollFunction
from solidago.primitives.decay import Decay, QuadraticDecay
from solidago.poll import *
from solidago.primitives.time import Date, DateInput, Duration, DurationInput
from solidago.primitives.datastructure import SelectLast


class Follows(PollFunction):
    default_follows: dict[str, float] = dict(follow=1.)
    default_follow_lifetime: Duration = Duration(weeks=52.*3)
    default_decay: Decay = QuadraticDecay(2.)

    def __init__(self,
        follows: dict[str, float] | None = None, 
        decay: Decay | tuple[str, dict] | None = None,
        follow_lifetime: DurationInput | None = None,
        username: str | None = None,
        date: DateInput | None = None,
    ):
        """ decay is directly in added to BaseVolumes because it also depends on self.follows """
        self.follows = self.default_follows if follows is None else follows
        import solidago, solidago.primitives.decay as d
        self.decay = solidago.load(decay, d, Decay, self.default_decay)
        fl = follow_lifetime
        self.follow_lifetime = self.default_follow_lifetime if fl is None else Duration(fl)
        self.username = username
        self.date = None if date is None else Date(date)

    def fn(self, users: Users, socials: Socials) -> VotingRights:
        if self.username is None:
            self.log_warning("Follows without receiver. Identity used instead.")
            return VotingRights(keynames=["username"]).add_columns(follow_volume=0)
        
        actions = socials.filters(by=self.username, kind=self.follows.keys())
        followed_usernames = list(set(actions("to")))
        voting_rights = VotingRights(followed_usernames, columns=["username"], keynames=["username"])

        actions_df = actions.df
        last_action_df = actions_df.loc[actions_df.groupby("to")["timestamp"].idxmax()]
        last_action_kinds = dict(zip(last_action_df["to"], last_action_df["kind"]))
        last_action_timestamps = dict(zip(last_action_df["to"], last_action_df["timestamp"]))
        if "weight" in last_action_df:
            last_action_weights = dict(zip(last_action_df["to"], last_action_df["weight"]))
        else:
            last_action_weights = {}

        follow_kinds = [last_action_kinds.get(n, "None") for n in followed_usernames]
        t = (Date.now() if self.date is None else self.date).timestamp()
        timestamps = np.array([last_action_timestamps.get(n, t) for n in followed_usernames])
        ages = t - timestamps
        weights = np.array([last_action_weights.get(n, 1.) for n in followed_usernames])
        decays = self.decay(ages, self.follow_lifetime.total_seconds)
        return voting_rights.add_columns(weight=weights, decay=decays, age=ages, 
            timestamp=timestamps, follow_kind=follow_kinds, follow_volume=weights * decays)