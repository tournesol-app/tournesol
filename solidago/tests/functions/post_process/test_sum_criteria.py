import pytest

from solidago import *
from solidago.poll.scoring import *


user_models = UserModels(
    user_directs=UserDirectScores([
        ("user_0", "entity_0", "default", 2, 1, .5),
        ("user_0", "entity_1", "post", 1, .2, .1),
        ("user_0", "entity_0", "repost", .2, .4, .3),
        ("user_0", "entity_1", "repost", .2, .4, .3),
        ("user_1", "entity_0", "default", -1.2, 1, .5),
        ("user_1", "entity_2", "report", -.3, .2, .1),
        ("user_1", "entity_2", "repost", .4, .4, .3),
    ], columns=["username", "entity_name", "criterion", "value", "left_unc", "right_unc"])
)
global_model = ScoringModel(
    directs=DirectScores([
        ("entity_0", "post", 1.2, 1, .5),
        ("entity_0", "report", -1.2, 1, .5),
        ("entity_1", "default", -.2, .5, .5),
        ("entity_2", "default", -.3, .2, .1),
        ("entity_2", "post", -.3, .2, .1),
        ("entity_2", "repost", -.3, .2, .1),
    ], columns=["entity_name", "criterion", "value", "left_unc", "right_unc"])
)

def test_sum_criteria():
    f = functions.post_process.SumCriteria(dict(post=1, repost=2, report=3), "main2")
    u, g = f.fn(user_models, global_model)
    e, c = Entity("entity_0"), "main2"
    assert u["user_0"](e, c) == Score((.4, .8, .6))
    assert g(e, c).to_triplet() == pytest.approx((-2.4, 4, 2), rel=1e-3)
