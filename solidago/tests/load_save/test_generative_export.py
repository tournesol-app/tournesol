import pytest
from solidago import *


def test_generative_model():
    with open("tests/generative_model/test_generative_model.json") as f: 
        generative_model = GenerativeModel.load(json.load(f))

    s = generative_model(seed=0)
    
    print("Saving data")
    s.save("tests/load_save/generated_state")
    
    print("Reloading saved data")
    s2 = State.load("tests/load_save/generated_state")
    
    assert "user_7" in s2.users
    assert s.users.get("user_5")["n_comparisons"] == s2.users.get("user_5")["n_comparisons"]
    assert s.vouches["user_4", "user_3", "Personhood"] == s2.vouches["user_4", "user_3", "Personhood"]
    assert "entity_3" in s2.entities
    assert len(s2.entities) == 20
    assert s.made_public["user_1"].get_set("entity_name") == s2.made_public["user_1"].get_set("entity_name")
    assert s.assessments["user_2", "default"].get_set("entity_name") == s2.assessments["user_2", "default"].get_set("entity_name")
    assert s.comparisons["user_0", "default", "entity_7"].get_set("right_name") == s2.comparisons["user_0", "default", "entity_7"].get_set("right_name")

