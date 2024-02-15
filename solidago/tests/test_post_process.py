import pytest
import numpy as np

from solidago.scoring_model import DirectScoringModel
from solidago.post_process import Squash


user_models = {
    0: DirectScoringModel({
        0: (2, 1, 0.5),
        1: (1, 0.2, .1),
        3: (0.2, .4, .3)
    }),
    1: DirectScoringModel({
        0: (-1.2, 1, .5),
        2: (-.3, .2, .1),
        3: (0.4, .4, .3)
    }),
}
global_model = DirectScoringModel({
    0: (-1.2, 1, .5),
    1: (-.2, .5, .5),
    2: (-.3, .2, .1),
    3: (0.4, .4, .3)
})

def test_squash():
    post_user_models, post_global_model = Squash(score_max=100)(user_models, global_model)
    assert post_user_models[0](1, None)[0] == pytest.approx(100/np.sqrt(2), 1e-3)

