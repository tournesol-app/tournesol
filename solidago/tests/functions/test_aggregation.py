import pytest
from solidago import *
from solidago.functions import Average, EntitywiseQrQuantile

N_SEEDS = 3

polls = [ Poll.load(f"tests/saved/{seed}") for seed in range(N_SEEDS) ]

entities = Entities(["entity_0", "entity_1", "entity_2", "entity_3"])
voting_rights = VotingRights()
voting_rights["user_0", "entity_0", "default"] = 1
voting_rights["user_0", "entity_1", "default"] = 1
voting_rights["user_0", "entity_3", "default"] = 1
voting_rights["user_1", "entity_0", "default"] = 1
voting_rights["user_1", "entity_2", "default"] = 1
voting_rights["user_1", "entity_3", "default"] = 1
user_models = UserModels(
    MultiScore(["username", "entity_name", "criterion"], {
        ("user_0", "entity_0", "default"): Score(2, 1, .5),
        ("user_0", "entity_1", "default"): Score(1, .2, .1),
        ("user_0", "entity_3", "default"): Score(.2, .4, .3),
        ("user_1", "entity_0", "default"): Score(-1.2, 1, .5),
        ("user_1", "entity_2", "default"): Score(-.3, .2, .1),
        ("user_1", "entity_3", "default"): Score(.4, .4, .3),
    }, name="user_directs")
)

def test_average_simple_instance():
    global_model = Average(max_workers=1)(entities, voting_rights, user_models)
    assert global_model("entity_0", "default").value == 0.4
    assert global_model("entity_1")["default"].value == 1
    assert global_model("entity_2")["default"].value == -.3
    assert global_model("entity_3", "default").to_triplet() == pytest.approx((0.3, .4, .3), abs=1e-2)

def test_qr_quantile_simple_instance():
    aggregator = EntitywiseQrQuantile(quantile=0.2, lipschitz=100, error=1e-5, max_workers=1)
    global_model = aggregator(entities, voting_rights, user_models)
    assert global_model("entity_0", "default").value < -1
    assert global_model("entity_1", "default").value == pytest.approx(1., abs=1e-2)
    assert global_model("entity_2", "default").value == pytest.approx(-.3, abs=1e-2)
    assert global_model("entity_3", "default").value > 0.2

@pytest.mark.parametrize( "seed", list(range(N_SEEDS)) )
def test_average(seed):
    _ = Average(max_workers=1).poll2objects_function(polls[seed])

@pytest.mark.parametrize( "seed", list(range(N_SEEDS)) )
def test_aggregation(seed):
    aggregator = EntitywiseQrQuantile(quantile=0.2, lipschitz=0.1, error=1e-5, max_workers=1)
    _ = aggregator.poll2objects_function(polls[seed])

