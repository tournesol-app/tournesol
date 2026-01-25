import pytest
from solidago import *


def test_generative_model():
    generator = load("tests/generators/test_generator.yaml")
    assert isinstance(generator, Generator)
    s1 = generator()
    
    s1.save("tests/load_save/generated_state")
    s2 = Poll.load("tests/load_save/generated_state")
    
    assert "user_1" in s2.users
    assert "entity_3" in s2.entities
    assert len(s2.entities) == 8

    f = lambda s: s.users["user_3"].n_evaluated_entities
    assert f(s1) == f(s2)

    f = lambda s: s.vouches["user_2", "user_3", "Personhood"]
    assert f(s1) == pytest.approx(f(s2), 1e-2)

    f = lambda s: s.made_public["user_1"].keys("entity_name")
    assert f(s1) == f(s2)

    f = lambda s: s.assessments["user_2", "default"].keys("entity_name")
    assert f(s1) == f(s2)

    f = lambda s: s.comparisons["user_0", "default", "entity_5"].keys("other_name")
    assert f(s1) == f(s2)

