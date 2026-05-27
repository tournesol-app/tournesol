from functools import reduce
import numpy as np

from solidago.poll import *
from solidago.functions.customizable import CustomizablePollFunction
from solidago.primitives.datastructure import Contains, After
from solidago.primitives.time import Date, DateInput, Duration, DurationInput


class Mentions(CustomizablePollFunction):
    default_age_cutoff: float = Duration(weeks=52).total_seconds

    def __init__(self, 
        mention_volume: float = .5,
        relative_max_volume: float = .2,
        age_cutoff: DurationInput | None = None,
        username: str | None = None,
        date: DateInput | None = None,
    ):
        """
        Parameters
        ----------
        mention_volume: float
            volume of a user that mentions the receiver
            Their actual volume may be larger if the user is already followed
            It may be lower if too many non-followed accounts mention the receiver
        relative_max_volume: float
            The total added volume through mentions must be a relative fraction
            of explicitly defined followed accounts, to guarantee receiver control
            over the volumes they allocate
        age_cutoff: dict[str, int] | int | None = None
            Could be e.g. dict(weeks=1)
            Mentions that are older than age_cutoff will be discarded
            Default value is 52 weeks
        """
        super().__init__(username, date)
        self.mention_volume = mention_volume
        self.relative_max_volume = relative_max_volume
        self.age_cutoff = self.default_age_cutoff
        if age_cutoff is not None:
            self.age_cutoff = Duration(age_cutoff).total_seconds

    def fn(self, users: Users, entities: Entities, voting_rights: VotingRights) -> VotingRights:
        if self.username is None:
            self.log_warning("Mentions without receiver. Returned no mention_volume.")
            return voting_rights.add_columns(mention_volume=0)
        
        follow_volumes = voting_rights("follow_volume", 0)
        t = (self.date or Date.now()).timestamp()
        min_timestamp = t - self.age_cutoff
        if "mentions" not in entities.columns:
            entities = entities.assign(mentions=[()] * len(entities))
        entities = entities.filters(mentions=Contains(self.username), timestamp=After(min_timestamp))
        mentioners = reduce(lambda acc, e: acc | set(e.get("authors", ())), entities, set())
        is_followed_mentioner = np.array([n in mentioners for n in voting_rights("username")])
        nonfollowed_mentioners = users.filters(m for m in mentioners if m not in voting_rights("username"))
        missing_volumes = self.mention_volume * is_followed_mentioner
        total_missing_volume = missing_volumes.sum() + len(nonfollowed_mentioners) * self.mention_volume
        if total_missing_volume == 0:
            return voting_rights.add_columns(mention_volume=0)
        multiplier = min(1., self.relative_max_volume * follow_volumes.sum() / total_missing_volume)
        mention_volumes = missing_volumes * multiplier
        voting_rights = voting_rights.add_columns(mention_volume=mention_volumes)
        nonfollowed_kwargs = dict(mention_volume=self.mention_volume * multiplier, follow_kind="mention")
        for mentioner in nonfollowed_mentioners:
            timestamp = entities.filters(authors=Contains(mentioner.name))("timestamp").max()
            voting_right = VotingRight(username=mentioner.name, timestamp=timestamp)
            voting_rights.append(voting_right, **nonfollowed_kwargs)
        voting_rights.set_columns(follow_volume=np.nan_to_num(voting_rights("follow_volume")))
        return voting_rights