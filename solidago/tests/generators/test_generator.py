import pytest
from solidago import *


def test_svd_user_generator():
    user_gen = generators.user.NormalUser(n_users=10, dimension=5)
    users = user_gen()
    assert len(users) == 10
    for user in users:
        assert user["is_trustworthy"] or not user["is_pretrusted"]

def test_erdos_renyi_vouch_generator():
    users = generators.user.NormalUser(n_users=10, p_trustworthy=0.8, p_pretrusted=0.2, dimension=5)()
    vouches = generators.vouch.ErdosRenyiVouch()(users)
    for (voucher_name, vouchee_name, kind), (weight, priority) in vouches:
        assert users.get(voucher_name)["is_trustworthy"] == users.get(vouchee_name)["is_trustworthy"]
    
def test_svd_entity_generator():
    entities = generators.entity.NormalEntity(n_entities=100, dimension=5)()
    assert len(entities) == 100

def test_evaluation_generator():
    users = generators.user.NormalUser(n_users=10, p_trustworthy=0.8, p_pretrusted=0.2, dimension=5)()
    entities = generators.entity.NormalEntity(n_entities=100, dimension=5)()
    made_public, assessments, comparisons = generators.engagement.SimpleEngagement()(users, entities)
    assessments = generators.assessment.NormalAssessment(error_size=2)(users, entities, made_public, assessments)
    comparisons = generators.comparison.KnaryGBT(21, 10)(users, entities, made_public, comparisons)
            
def test_generative_model():
    for seed in range(5):
        state = State.load(f"tests/modules/saved/{seed}")
        for key in ("users", "entities", "vouches", "made_public", "assessments", "comparisons"):
            assert len(getattr(state, key)) > 0
