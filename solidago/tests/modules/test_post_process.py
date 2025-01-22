import pytest
import numpy as np

from solidago import *
from solidago.modules.post_process import Squash


user_models = UserModels({
    "user_0": DirectScoring({
        "entity_0": { "default": (2, 1, 0.5) },
        "entity_1": { "default": (1, 0.2, .1) },
        "entity_3": { "default": (0.2, .4, .3) }
    }),
    "user_1": DirectScoring({
        "entity_0": { "default": (-1.2, 1, .5) },
        "entity_2": { "default": (-.3, .2, .1) },
        "entity_3": { "default": (0.4, .4, .3) }
    }),
})
global_model = DirectScoring({
    "entity_0": { "default": (-1.2, 1, .5) },
    "entity_1": { "default": (-.2, .5, .5) },
    "entity_2": { "default": (-.3, .2, .1) },
    "entity_3": { "default": (0.4, .4, .3) }
})

def test_squash():
    post_user_models, post_global_model = Squash(score_max=100)(user_models, global_model)
    assert post_user_models["user_0"]("entity_1")["default"].value == pytest.approx(100/np.sqrt(2), 1e-3)

