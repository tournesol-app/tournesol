import pytest
from solidago import *

states = [ State.load(f"tests/pipeline/saved_{seed}") for seed in range(5) ]

entities = Entities(["entity_0", "entity_1", "entity_2", "entity_3"])
voting_rights = VotingRights()
voting_rights["user_0", "entity_0", "default"] = 1
voting_rights["user_0", "entity_1", "default"] = 1
voting_rights["user_0", "entity_3", "default"] = 1
voting_rights["user_1", "entity_0", "default"] = 1
voting_rights["user_1", "entity_2", "default"] = 1
voting_rights["user_1", "entity_3", "default"] = 1
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

def test_average_simple_instance():
    global_model = Average()(entities, voting_rights, user_models)
    assert global_model("entity_0")["default"].value == 0.4
    assert global_model("entity_1")["default"].value == 1
    assert global_model("entity_2")["default"].value == -.3
    assert global_model("entity_3")["default"].to_triplet() == pytest.approx((0.3, .4, .3), abs=1e-2)

def test_qr_quantile_simple_instance():
    aggregator = EntitywiseQrQuantile(quantile=0.2, lipschitz=100, error=1e-5)
    global_model = aggregator(entities, voting_rights, user_models)
    assert global_model("entity_0")["default"].value < -1
    assert global_model("entity_1")["default"].value == pytest.approx(1., abs=1e-2)
    assert global_model("entity_2")["default"].value == pytest.approx(-.3, abs=1e-2)
    assert global_model("entity_3")["default"].value > 0.2

@pytest.mark.parametrize( "seed", list(range(5)) )
def test_average(seed):
    global_model = Average().state2objects_function(states[seed])

@pytest.mark.parametrize( "seed", list(range(5)) )
def test_aggregation(seed):
    aggregator = EntitywiseQrQuantile(quantile=0.2, lipschitz=0.1, error=1e-5)
    global_model = aggregator.state2objects_function(states[seed])

