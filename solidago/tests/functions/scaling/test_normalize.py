import numpy as np
import pytest

from solidago import *
from solidago.poll.scoring import *


users = Users(["user_0", "user_1"])
entities = Entities(["entity_0", "entity_1", "entity_2", "entity_3"])
public_settings = PublicSettings()
user_models = UserModels(
    user_directs=UserDirectScores([
        ("user_0", "entity_0", "post", 2, 1, .5),
        ("user_0", "entity_1", "repost", 1, .2, .1),
        ("user_0", "entity_3", "repost", .2, .4, .3),
        ("user_1", "entity_0", "report", -1.2, 1, .5),
        ("user_1", "entity_2", "report", -.3, .2, .1),
        ("user_1", "entity_3", "post", .4, .4, .3),
        ("user_2", "entity_2", "repost", .3, .2, .1),
        ("user_2", "entity_3", "repost", .4, .4, .3),
    ], columns=["username", "entity_name", "criterion", "value", "left_unc", "right_unc"])
)


def test_normalize():
    normalize = functions.scaling.Normalize(dict(repost=2, report=float("inf")), 1)
    scaled = normalize.fn(entities, user_models)
    f = lambda u, e, c: scaled[u](Entity(e), c).value
    assert len(user_models) == len(scaled)
    assert f("user_0", "entity_0", "post") == pytest.approx(1., 1e-3)
    assert np.isnan(f("user_0", "entity_3", "post"))
    assert f("user_0", "entity_1", "repost") == pytest.approx(.98058, 1e-3)
    assert f("user_0", "entity_3", "repost") == pytest.approx(.196116, 1e-3)
    assert f("user_1", "entity_0", "report") == pytest.approx(-1., 1e-3)
    assert f("user_1", "entity_2", "report") == pytest.approx(-0.25, 1e-3)
    assert f("user_1", "entity_3", "post") == pytest.approx(1., 1e-3)
    assert f("user_2", "entity_2", "repost") == pytest.approx(.6, 1e-3)
    assert f("user_2", "entity_3", "repost") == pytest.approx(.8, 1e-3)


def test_max_normalize():
    normalize = functions.scaling.MaxNorm(dict(repost=2, report=float("inf")), default_q=1)
    scaled = normalize.fn(entities, user_models)
    f = lambda u, e, c: scaled[u](Entity(e), c).value
    assert len(user_models) == len(scaled)
    assert f("user_0", "entity_0", "post") == pytest.approx(1., 1e-3)
    assert np.isnan(f("user_0", "entity_3", "post"))
    assert f("user_0", "entity_1", "repost") == pytest.approx(.98058, 1e-3)
    assert f("user_0", "entity_3", "repost") == pytest.approx(.196116, 1e-3)
    assert f("user_1", "entity_0", "report") == pytest.approx(-1., 1e-3)
    assert f("user_1", "entity_2", "report") == pytest.approx(-0.25, 1e-3)
    assert f("user_1", "entity_3", "post") == pytest.approx(.4, 1e-3)
    assert f("user_2", "entity_2", "repost") == pytest.approx(.3, 1e-3)
    assert f("user_2", "entity_3", "repost") == pytest.approx(.4, 1e-3)