import pytest
import numpy as np

from solidago import *
from solidago.poll.scoring import *
from solidago.primitives.decay import QuadraticDecay


user_models = UserModels(
    user_directs=UserDirectScores([
        ("user_0", "entity_0", 10, "default", 2, 1, .5),
        ("user_0", "entity_1", 15, "post", 1, .2, .1),
        ("user_0", "entity_0", 21, "repost", .2, .4, .3),
        ("user_0", "entity_1", 32, "repost", .2, .4, .3),
        ("user_1", "entity_0", 52, "default", -1.2, 1, .5),
        ("user_1", "entity_2", 63, "report", -.3, .2, .1),
        ("user_1", "entity_2", 35, "repost", .4, .4, .3),
    ], columns=[
        "username", "entity_name", "date", "criterion", "value", "left_unc", "right_unc"
    ])
)

def test_time_decay():
    decay = QuadraticDecay(multiplier=2.)
    decay_bias = functions.preference_bias.TimeDecay(decay, 10, 83)
    b = decay_bias.fn(user_models)
    f = lambda biased_models, u, e, c: biased_models[u](Entity(e), c).value
    g = lambda lt, v, d: pytest.approx(2 * v * lt**2 / (lt**2 + (83-d)**2), 1e-3)
    assert f(b, "user_0", "entity_0", "default") == g(10, 2, 10)
    assert f(b, "user_0", "entity_1", "post") == g(10, 1, 15)
    assert f(b, "user_0", "entity_1", "repost") == g(10, .2, 32)
    assert f(b, "user_1", "entity_0", "default") == g(10, -1.2, 52)
    assert f(b, "user_1", "entity_2", "report") == g(10, -.3, 63)
    assert f(b, "user_1", "entity_2", "repost") == g(10, .4, 35)
    assert np.isnan(f(b, "user_1", "entity_2", "default"))
    assert f(b, "user_0", "entity_0", "repost") == g(10, .2, 21)
    