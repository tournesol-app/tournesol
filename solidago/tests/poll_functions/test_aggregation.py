import pytest
from solidago import *
from solidago.poll.scoring import *

entities = Entities(["entity_0", "entity_1", "entity_2", "entity_3"])
voting_rights = VotingRights()
voting_rights.set(username="user_0", entity_name="entity_0", criterion="default", voting_right=1)
voting_rights.set(username="user_0", entity_name="entity_1", criterion="default", voting_right=1)
voting_rights.set(username="user_1", entity_name="entity_0", criterion="default", voting_right=1)
voting_rights.set(username="user_1", entity_name="entity_2", criterion="default", voting_right=1)
voting_rights.set(username="user_1", entity_name="entity_3", criterion="default", voting_right=1)
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

def test_step_by_step_average():
    average = poll_functions.Average(max_workers=1)
    kwargs, variables, nonargs_lists, args_lists = average.precompute(entities, voting_rights, user_models)

def test_average_simple_instance():
    global_model = poll_functions.Average(max_workers=1)(entities, voting_rights, user_models)
    assert global_model(entities["entity_0"], "default").value == 0.4
    assert global_model(entities["entity_1"]).get(criterion="default").value == 1
    assert global_model(entities["entity_2"]).get(criterion="default").value == -.3
    assert global_model(entities["entity_3"], "default").to_triplet() == pytest.approx((0.3, .4, .3), abs=1e-2)

def test_qr_quantile_simple_instance():
    aggregator = poll_functions.EntitywiseQrQuantile(quantile=0.2, lipschitz=100, error=1e-5, max_workers=1)
    global_model = aggregator(entities, voting_rights, user_models)
    assert global_model(entities["entity_0"], "default").value < -1
    assert global_model(entities["entity_1"], "default").value == pytest.approx(1., abs=1e-2)
    assert global_model(entities["entity_2"], "default").value == pytest.approx(-.3, abs=1e-2)
    assert global_model(entities["entity_3"], "default").value > 0.2

