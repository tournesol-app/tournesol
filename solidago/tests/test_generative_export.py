import pytest
from solidago import *


def generative_model():
    with open("experiments/toy.json") as f: hps = json.load(f)
    gen = GenerativeModel.load(hps["generative_model"])
        
    users = gen.user_gen(30)
    vouches = gen.vouch_gen(users)
    entities = gen.entity_gen(100)
    criteria = gen.criterion_gen(2)
    made_public, assessments, comparisons = gen.engagement_gen(users, entities, criteria)
    assessments = gen.assessment_gen(users, entities, criteria, made_public, assessments)
    comparisons = gen.comparison_gen(users, entities, criteria, made_public, comparisons)
    
    s = generative_model(30, 100, 2, 0)
    
    print("Saving data")
    s.save("experiments/generated_model")
    
    print("Reloading saved data")
    s2 = State.load("experiments/generated_model")
    
    assert "17" in s2.users
    assert s.users.get("10")["n_comparisons"] == s2.users.get("10")["n_comparisons"]
    assert s.vouches["24", "11", "ProofOfPersonhood"] == s2.vouches["24", "11", "ProofOfPersonhood"]
    assert "73" in s2.entities
    assert len(s2.entities) == 100
    assert "1" in s2.criteria
    assert len(s2.criteria) == 2
    assert s.made_public["21"] == s2.made_public["21"]
    assert set(s.assessments["12", "0"]["entity_name"]) == set(s2.assessments["12", "0"]["entity_name"])
    assert set(s.comparisons["0", "0", "57"]["as_left"].keys()) == set(s2.comparisons["0", "0", "57"]["as_left"].keys())

