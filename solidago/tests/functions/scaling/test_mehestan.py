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


def test_mehestan():
    mehestan = functions.scaling.Mehestan(max_workers=1)
    scaled_users, scaled = mehestan.fn(users, entities, public_settings, user_models)
    assert len(scaled_users) == len(users)
    assert len(user_models) == len(scaled)