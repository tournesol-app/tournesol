from functools import reduce

from solidago.poll import *
from solidago.functions.customizable import CustomizablePollFunction
from solidago.primitives.datastructure import Contains, After
from solidago.primitives.time import Date, DateInput, Duration, DurationInput


class Mentions(CustomizablePollFunction):
    default_age_cutoff: Duration = Duration(weeks=52)

    def __init__(self, 
        mention_volume: float = .5,
        relative_max_volume: float = .2,
        age_cutoff: DurationInput | None = None,
        receiver: User | None = None,
        date: DateInput | None = None,
    ):
        """
        Parameters
        ----------
        mention_volume: float
            volume of a user that mentions the receiver
            Their actual volume may be larger if the user is already a councillor
            It may be lower if too many noncouncillors mention the receiver
        relative_max_volume: float
            The total added volume through mentions must be a relative fraction
            of explicitly defined councillors, to guarantee receiver control
            over the volumes they allocate
        age_cutoff: dict[str, int] | int | None = None
            Could be e.g. dict(weeks=1)
            Mentions that are older than age_cutoff will be discarded
            Default value is 52 weeks
        """
        super().__init__(receiver, date)
        self.mention_volume = mention_volume
        self.relative_max_volume = relative_max_volume
        self.age_cutoff = self.default_age_cutoff
        if age_cutoff is not None:
            self.age_cutoff = Duration(age_cutoff)

    def fn(self, users: Users, entities: Entities) -> Users:        
        if self.receiver is None:
            self.log_warning("Mentions without receiver. Identity used instead.")
            return users
        
        follow_volumes = users("follow_volume", 0)
        date = self.date or Date.now()
        min_date = (date - self.age_cutoff).timestamp()
        entities = entities.filters(mentions=Contains(self.receiver.name), date=After(min_date))
        mentioners = reduce(lambda acc, e: acc | set(e["authors"]), entities, set())
        is_mentioner = users.names().isin(mentioners)
        missing_volumes = (self.mention_volume - follow_volumes).clip(0) * is_mentioner
        multiplier = min(1., self.relative_max_volume * follow_volumes.sum() / missing_volumes.sum())
        mention_volumes = missing_volumes * multiplier
        return users.assign(mention_volume=mention_volumes)