import pytest
from solidago import Generator, Poll

N_SEEDS = 3

def test_generative_model():
    generator = Generator.load("tests/generators/test_generator.yaml")
    s1 = generator.fn()
    
    s1.save("tests/save_load/saved/test_generative")
    s2 = Poll.load("tests/save_load/saved/test_generative")
    
    assert "user_1" in s2.users
    assert "entity_3" in s2.entities
    assert len(s2.entities) == 8

    f = lambda s: s.users["user_3"]["n_evaluated_entities"]
    assert f(s1) == f(s2)

    f = lambda s: s.socials.get(by="user_2", to="user_3", kind="Personhood")["weight"]
    assert f(s1) == pytest.approx(f(s2), 1e-2)

    f = lambda s: s.public_settings.filters(username="user_1").keys("entity_name")
    assert f(s1) == f(s2)

    f = lambda s: s.ratings.filters(username="user_2", criterion="default").keys("entity_name")
    assert f(s1) == f(s2)

    f = lambda s: s.comparisons.filters(username="user_0", criterion="default", left_name="entity_5").keys("right_name")
    assert f(s1) == f(s2)
