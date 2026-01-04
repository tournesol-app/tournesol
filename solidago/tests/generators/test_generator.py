from solidago import *
from solidago.generators.engagements.select_entities import BiasedByScore
from solidago.primitives.random import Normal, Bernoulli, Zipf, Add, Poisson, Uniform

N_SEEDS = 3

def test_svd_user_generator():
    n_users = 10
    users = generators.users.Users(n_users, Normal(5))()
    users = generators.users.AddColumn("is_trustworthy", Bernoulli(0.8))(users)
    users = generators.users.BernoulliPretrust(0.2)(users)
    assert len(users) == n_users
    for user in users:
        assert user["is_trustworthy"] or not user["is_pretrusted"]

def test_erdos_renyi_vouch_generator():
    n_users = 10
    users = generators.users.Users(n_users, Normal(5))()
    users = generators.users.AddColumn("is_trustworthy", Bernoulli(0.8))(users)
    users = generators.users.BernoulliPretrust(0.2)(users)
    users = generators.users.AddColumn("expected_n_vouches", Zipf(1.5))(users)
    vouches = generators.vouches.ErdosRenyi()(users)
    for (voucher_name, vouchee_name, kind), (weight, priority) in vouches:
        assert users[voucher_name].is_trustworthy == users[vouchee_name].is_trustworthy
    
def test_svd_entity_generator():
    entities = generators.entities.Entities(100, Normal(5))()
    assert len(entities) == 100

def test_evaluation_generator():
    users = generators.users.Users(10, Normal(5))()
    entities = generators.entities.Entities(100, Normal(5))()

    users = generators.users.AddColumn("n_evaluated_entities", Add([Zipf(1.5), Poisson(3.0)]))(users)
    users = generators.users.AddColumn("engagement_bias", Normal())(users)
    users = generators.users.AddColumn("p_public", Uniform())(users)
    users = generators.users.AddColumn("p_assess", Uniform())(users)
    users = generators.users.AddColumn("n_comparisons_per_entity", Uniform(1.0, 5.0))(users)

    engagement_generator = generators.engagements.Independent(BiasedByScore(Normal()))
    made_public, assessments, comparisons = engagement_generator(users, entities)
    assessments = generators.assessments.Independent(
        generators.assessments.Noisy(Normal())
    )(users, entities, made_public, assessments)
    comparisons = generators.comparisons.Independent(
        generators.comparisons.KnaryGBT(21, 10)
    )(users, entities, made_public, comparisons)
    assert len(assessments) > 0
    assert len(comparisons) > 0
            
def test_generative_model():
    for seed in range(N_SEEDS):
        state = Poll.load(f"tests/saved/{seed}")
        for key in ("users", "entities", "vouches", "made_public", "assessments", "comparisons"):
            assert len(getattr(state, key)) > 0
