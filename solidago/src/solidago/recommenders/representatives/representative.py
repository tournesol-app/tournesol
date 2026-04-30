from abc import abstractmethod
from solidago.poll import *
from .base import BaseBallots
from .bias import BallotBiasing

class Representative:
    default_default_lifetime: dict = dict(weeks=1)

    def __init__(self, 
        poll: Poll, 
        councillor: User | str, 
        base_ballots: BaseBallots | tuple[str, dict],
        biases: list[BallotBiasing | tuple[str, dict]] | None,
        default_lifetime: dict | None = None,
        lifetime_bias: float = 0.,
        criteria_weights: dict | None = None,
    ):
        self.poll = poll
        self.councillor = poll.users[councillor]
        import solidago, solidago.recommenders.representatives as r
        self.base_ballots = solidago.load(base_ballots, r.base, BaseBallots, r.base.Direct(self.councillor))
        self.biases = solidago
        
        default_lifetime = default_lifetime or self.default_default_lifetime
        self.default_lifetime = timedelta(**default_lifetime)
        self.lifetime_bias = lifetime_bias
        self.criteria_weights = criteria_weights or self.default_criteria_weights

    def time_decay(self, date: int, lifetime: int) -> float:
        """ date and lifetime must be given in seconds """
        age = date - datetime.now().second
        decay = lifetime / (age**2 + lifetime**2)
        if lifetime != 0 and lifetime != self.default_lifetime.seconds:
            log = np.log(1 + lifetime / self.default_lifetime.seconds)
            decay *= np.power(log, self.lifetime_bias)
        return decay

    def __call__(self, target_user: User | None = None) -> Scores:
        scores = Scores(keynames=["entity_name"])
        
        for e in self.poll.entities.filters(author=self.user.name):
            lifetime = e["lifetime"] if "lifetime" in e else self.default_lifetime.seconds
            score = self.time_decay(e["date"], lifetime)
            scores.append(Score(score), entity_name=e.name, date=e["date"])

        kwargs = dict(username=self.user.name, criterion=self.criteria_weights.keys())
        for r in self.poll.ratings.filters(**kwargs):
            name, date = r["entity_name"], r["timestamp"]
            if target_user is not None and self.poll.entities[name]["author"] == target_user.name:
                continue
            if name not in scores.keys("entity_name") or date > scores.get(entity_name=name)["timestamp"]:
                lifetime = r["lifetime"] if "lifetime" in r else self.default_lifetime.seconds
                score = self.time_decay(date, lifetime)
                scores.append(Score(score), entity_name=name, date=date)

        return scores

    @abstractmethod
    def __call__(self, target_user: User | None = None) -> Scores:
        raise NotImplemented
