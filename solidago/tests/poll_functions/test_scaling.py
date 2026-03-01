import numpy as np

from solidago import *
from solidago.poll.scoring import *


users = Users(["user_0", "user_1"])
entities = Entities(["entity_0", "entity_1", "entity_2", "entity_3"])
public_settings = PublicSettings()
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


def test_learned_models():
    scaled_users, scaled = poll_functions.Mehestan(max_workers=1)(users, entities, public_settings, user_models)
    assert len(scaled_users) == len(users)
    assert len(user_models) == len(scaled)

def test_standardize():
    standardized_models = poll_functions.LipschitzStandardize(lipschitz=1000, max_workers=1)(entities, user_models)
    values = standardized_models().value
    deviations = np.abs(values - np.median(values))
    quantile = int(0.9 * len(deviations))
    assert deviations[np.argsort(deviations)[quantile]] < 3
    assert deviations[np.argsort(deviations)[quantile]] > 0.5
    
def test_quantile_shift():
    quantile_shift = poll_functions.LipschitzQuantileShift(lipschitz=1000, max_workers=1)
    base_models = UserModels(user_directs=user_models.user_directs)
    shifted_models = quantile_shift(entities, base_models)
    assert np.median(shifted_models().value) > 0

