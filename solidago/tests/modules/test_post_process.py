import pytest
import numpy as np

from solidago import *
from solidago.modules.post_process import Squash


user_models = UserModels(
    MultiScore(["username", "entity_name", "criterion"], {
        ("user_0", "entity_0", "default"): Score(2, 1, .5),
        ("user_0", "entity_1", "default"): Score(1, .2, .1),
        ("user_0", "entity_3", "default"): Score(.2, .4, .3),
        ("user_1", "entity_0", "default"): Score(-1.2, 1, .5),
        ("user_1", "entity_2", "default"): Score(-.3, .2, .1),
        ("user_1", "entity_3", "default"): Score(.4, .4, .3),
    })
)
global_model = ScoringModel(
    directs=MultiScore(["entity_name", "criterion"], {
        ("entity_0", "default"): Score(-1.2, 1, .5),
        ("entity_1", "default"): Score(-.2, .5, .5),
        ("entity_2", "default"): Score(-.3, .2, .1),
        ("entity_3", "default"): Score(.4, .4, .3),
    })
)

def test_squash():
    post_user_models, post_global_model = Squash(score_max=100)(user_models, global_model)
    assert post_user_models["user_0"]("entity_1", "default").value == pytest.approx(100/np.sqrt(2), 1e-3)

