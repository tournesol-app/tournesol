from numpy.typing import NDArray

from solidago.functions.poll_function import PollFunction
from solidago.functions.preference_bias.bias import PreferenceBias
from solidago.primitives.decay import Decay, QuadraticDecay
from solidago.poll import *
from solidago.primitives.time import Date, DateInput, Duration, DurationInput


class TimeDecay(PollFunction):
    default_decay: QuadraticDecay = QuadraticDecay(2.)
    default_default_lifetime: Duration = Duration(days=1)

    def __init__(self,
        decay: Decay | tuple[str, dict] | None = None,
        default_lifetime: DurationInput | None = None,
        date: DateInput | None = None,
        max_workers: int | None = None,
    ):
        super().__init__(max_workers)
        self.date = None if date is None else Date(date)
        import solidago, solidago.primitives.decay as d
        self.decay = solidago.load(decay, d, Decay, self.default_decay)
        self.default_lifetime = self.default_default_lifetime
        if default_lifetime is not None:
            self.default_lifetime = Duration(default_lifetime)

    def fn(self, user_models: UserModels) -> UserModels:
        scores = user_models()
        date = Date.now().timestamp() if self.date is None else self.date.timestamp()
        ages = date - scores("timestamp", 0)
        lifetimes = self.default_lifetime.total_seconds
        if "lifetime" in scores.columns:
            lifetimes = scores("lifetime")
        multipliers = self.decay(ages, lifetimes)
        user_models = UserModels(
            user_directs=UserDirectScores(
                dict(
                    username=scores("username"),
                    entity_name=scores("entity_name"),
                    criterion=scores("criterion"),
                    value=scores.value * multipliers
                ),
                keynames=scores.keynames,
                columns=["username", "entity_name", "criterion", "value"]
            )
        )
        if "timestamp" in scores.columns:
            user_models.user_directs.add_columns(timestamp=scores("timestamp"))
        if "left_unc" in scores.columns:
            user_models.user_directs.add_columns(left_unc=scores.left_unc * multipliers)
        if "right_unc" in scores.columns:
            user_models.user_directs.add_columns(right_unc=scores.right_unc * multipliers)
        return user_models
