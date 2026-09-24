import pytest
from solidago import *
from solidago.poll.scoring import *

entities = Entities(["entity_0", "entity_1", "entity_2", "entity_3"])
voting_rights = VotingRights()
voting_rights.set(username="user_0", entity_name="entity_0", criterion="default", voting_right=1)
voting_rights.set(username="user_0", entity_name="entity_1", criterion="default", voting_right=1)
voting_rights.set(username="user_0", entity_name="entity_3", criterion="default", voting_right=1)
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

def test_average():
    global_model = functions.aggregation.Average(max_workers=1).fn(entities, voting_rights, user_models)
    assert global_model(entities["entity_0"], "default").value == 0.4
    assert global_model(entities["entity_1"]).get(criterion="default").value == 1
    assert global_model(entities["entity_2"]).get(criterion="default").value == -.3
    assert global_model(entities["entity_3"], "default").to_triplet() == pytest.approx((0.3, .4, .3), abs=1e-2)

def test_qr_quantile():
    aggregator = functions.aggregation.EntitywiseQrQuantile(quantile=0.2, lipschitz=100, error=1e-5, max_workers=1)
    global_model = aggregator.fn(entities, voting_rights, user_models)
    assert global_model(entities["entity_0"], "default").value < -1
    assert global_model(entities["entity_1"], "default").value == pytest.approx(1., abs=1e-2)
    assert global_model(entities["entity_2"], "default").value == pytest.approx(-.3, abs=1e-2)
    assert global_model(entities["entity_3"], "default").value > 0.2

def test_sum():
    global_model = functions.aggregation.Sum(max_workers=1).fn(entities, voting_rights, user_models)
    assert global_model(entities["entity_0"], "default").value == 0.8
    assert global_model(entities["entity_1"]).get(criterion="default").value == 1
    assert global_model(entities["entity_2"]).get(criterion="default").value == -.3
    assert global_model(entities["entity_3"], "default").to_triplet() == pytest.approx((0.6, .8, .6), abs=1e-2)

def qr_quantile_uncertainty(n_users: int, value: float) -> float:
    """ n_users all score entity_0 at value, with uncertainty 0.5 """
    agreeing_entities = Entities(["entity_0"])
    agreeing_voting_rights = VotingRights()
    rows = list()
    for index in range(n_users):
        agreeing_voting_rights.set(username=f"user_{index}", entity_name="entity_0", criterion="default", voting_right=1)
        rows.append((f"user_{index}", "entity_0", "default", value, .5, .5))
    agreeing_user_models = UserModels(user_directs=UserDirectScores(
        rows, columns=["username", "entity_name", "criterion", "value", "left_unc", "right_unc"]
    ))
    aggregator = functions.aggregation.EntitywiseQrQuantile(quantile=0.2, lipschitz=0.1, error=1e-5, max_workers=1)
    global_model = aggregator.fn(agreeing_entities, agreeing_voting_rights, agreeing_user_models)
    return global_model(agreeing_entities["entity_0"], "default").left_unc

@pytest.mark.parametrize("value", [1., 7.])
def test_qr_quantile_uncertainty_decreases_with_agreeing_users(value):
    uncertainties = [qr_quantile_uncertainty(n_users, value) for n_users in (1, 6, 20)]
    assert uncertainties[0] > uncertainties[1] > uncertainties[2], uncertainties


