import pytest
from solidago import *


def test_generative_model():
    with open("tests/load_save/test_generative_model.json") as f: 
        generative_model = GenerativeModel.load(json.load(f))
            
    s = generative_model()
    
    print("Saving data")
    s.save("tests/load_save/generated_state")
    
    print("Reloading saved data")
    s2 = State.load("tests/load_save/generated_state")
    
    assert "17" in s2.users
    assert s.users.get("10")["n_comparisons"] == s2.users.get("10")["n_comparisons"]
    assert s.vouches["24", "11", "ProofOfPersonhood"] == s2.vouches["24", "11", "ProofOfPersonhood"]
    assert "73" in s2.entities
    assert len(s2.entities) == 100
    assert s.made_public["21"].get_set("entity_name") == s2.made_public["21"].get_set("entity_name")
    assert set(s.assessments["12", "0"]["entity_name"]) == set(s2.assessments["12", "0"]["entity_name"])
    assert set(s.comparisons["0", "0", "57"]["as_left"]) == set(s2.comparisons["0", "0", "57"]["as_left"])

