from copy import deepcopy

import pytest
import numpy as np

from solidago import *
from solidago.poll.scoring import *


user_models = UserModels(
    user_directs=UserDirectScores([
        ("user_0", "entity_0", "default", 2, 1, .5),
        ("user_0", "entity_1", "default", 1, .2, .1),
        ("user_0", "entity_3", "default", .2, .4, .3),
        ("user_1", "entity_0", "default", -1.2, 1, .5),
        ("user_1", "entity_2", "default", -.3, .2, .1),
        ("user_1", "entity_3", "default", .4, .4, .3),
    ], columns=["username", "entity_name", "criterion", "value", "left_unc", "right_unc"])
)
global_model = ScoringModel(
    directs=DirectScores([
        ("entity_0", "default", -1.2, 1, .5),
        ("entity_1", "default", -.2, .5, .5),
        ("entity_2", "default", -.3, .2, .1),
        ("entity_3", "default", .4, .4, .3),
    ], columns=["entity_name", "criterion", "value", "left_unc", "right_unc"])
)

def test_step_by_step_squash():
    """ criteria is not used """
    scores = user_models()
    assert isinstance(scores, Scores), scores 
    squashed_scores = deepcopy(scores)
    squash = SquashProcessing(max=100)
    value, min, max = squash.squash(scores.value), squash.squash(scores.min), squash.squash(scores.max)
    left_unc, right_unc = value - min, max - value
    squashed_scores.set_columns(value=value, left_unc=left_unc, right_unc=right_unc)
    assert all(np.isfinite(v) for v in squashed_scores.value)
    assert all(-100 <= v and v <= 100 for v in squashed_scores.value)
    assert all(np.isfinite(l) for l in squashed_scores.left_unc)
    assert all(-100 <= m and m <= 100 for m in squashed_scores.value - squashed_scores.left_unc)
    assert all(np.isfinite(r) for r in squashed_scores.right_unc)
    assert all(-100 <= m and m <= 100 for m in squashed_scores.value + squashed_scores.right_unc)

def test_squash():
    post_user_models, _ = poll_functions.Squash(score_max=100).fn(user_models, global_model)
    score = post_user_models["user_0"](Entity("entity_1"), "default")
    assert score.value == pytest.approx(100/np.sqrt(2), 1e-3)

