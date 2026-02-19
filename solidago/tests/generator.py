from solidago import *

from solidago.generators.engagements.select_entities import BiasedByScore
import solidago.generators.users as users
import solidago.generators.entities as entities
import solidago.generators.vouches as vouches
import solidago.generators.engagements as engagements
import solidago.generators.ratings as ratings
import solidago.generators.comparisons as comparisons

import solidago.primitives.random as random
from solidago.primitives.random import Normal, Multinomial, Bernoulli, Zipf, Poisson

_modules = [
    # User and entity generation
    users.New(5, Normal(dimension=5)),
    entities.New(8, Normal(dimension=5)),
    entities.AddColumn("author", Multinomial(
        probabilities=[.2, .3, .5],
        values=["Science4All", "Après La Bière", "La Fabrique Sociale"],
    )),
    entities.AddColumn("journalism", Multinomial(probabilities=[.4, .6], values=["True", "False"])),
    # User trust generation
    users.AddColumn("is_trustworthy", Bernoulli(0.8)),
    users.BernoulliPretrust(p_if_trustworthy=.2, p_if_untrustworthy=0.),
    # Vouch generation
    users.AddColumn("expected_n_vouches", Zipf(power_decay=2.)),
    vouches.ErdosRenyi(),
    # Engagement generation
    users.AddColumn("n_evaluated_entities", random.Add([Zipf(power_decay=2.), Poisson(mean=.5)])),
    users.AddColumn("engagement_bias", Normal()),
    users.AddColumn("p_public", random.Uniform()),
    users.AddColumn("p_rate", random.Uniform(.2, 1.)),
    users.AddColumn("n_comparisons_per_entity", random.Uniform(1., 5.)),
    engagements.Independent(BiasedByScore(Normal())),
    # Expression generation
    users.AddColumn("translation", Normal()),
    users.AddColumn("multiplier", random.Gamma(1., 1.)),
    # Ratings and comparisons
    ratings.Independent(ratings.Noisy(Normal()), ratings.Negate(ratings.Deterministic())),
    comparisons.Independent(comparisons.KnaryGBT(21, 10), comparisons.Negate(comparisons.KnaryGBT(21, 10)))
]

class TestGenerator(Generator):
    def __init__(self, max_workers: int = 1, seed: int | None = None):
        super().__init__(_modules, max_workers, seed)
