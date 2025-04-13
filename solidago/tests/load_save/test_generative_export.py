import pytest
from solidago import *
import json 


def test_generative_model():
    with open("tests/generators/test_generator.json") as f: 
        generator = Generator.load(json.load(f))

    s = generator(seed=0)
    
    s.save("tests/load_save/generated_state")
    s2 = State.load("tests/load_save/generated_state")
    
    assert "user_7" in s2.users
    assert s.users["user_5"].n_comparisons == s2.users["user_5"].n_comparisons
    assert s.vouches["user_4", "user_3", "Personhood"] == s2.vouches["user_4", "user_3", "Personhood"]
    assert "entity_3" in s2.entities
    assert len(s2.entities) == 20
    assert s.made_public["user_1"].keys("entity_name") == s2.made_public["user_1"].keys("entity_name")
    assert s.assessments["user_2", "default"].keys("entity_name") == s2.assessments["user_2", "default"].keys("entity_name")
    assert s.comparisons["user_0", "default", "entity_7"].keys("other_name") == s2.comparisons["user_0", "default", "entity_7"].keys("other_name")

