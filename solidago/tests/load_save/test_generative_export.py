import pytest
from solidago import load, Generator, Poll

N_SEEDS = 3

def test_generative_model():
    generator = load("tests/generators/test_generator.yaml")
    assert isinstance(generator, Generator)
    s1 = generator()
    
    s1.save("tests/load_save/generated_state")
    s2 = Poll.load("tests/load_save/generated_state")
    
    assert "user_1" in s2.users
    assert "entity_3" in s2.entities
    assert len(s2.entities) == 8

    f = lambda s: s.users["user_3"]["n_evaluated_entities"]
    assert f(s1) == f(s2)

    f = lambda s: s.vouches.get(by="user_2", to="user_3", kind="Personhood")["weight"]
    assert f(s1) == pytest.approx(f(s2), 1e-2)

    f = lambda s: s.public_settings.filters(username="user_1").keys("entity_name")
    assert f(s1) == f(s2)

    f = lambda s: s.ratings.filters(username="user_2", criterion="default").keys("entity_name")
    assert f(s1) == f(s2)

    f = lambda s: s.comparisons.filters(username="user_0", criterion="default", left_name="entity_5").keys("right_name")
    assert f(s1) == f(s2)

def test_generative_model2():
    for seed in range(N_SEEDS):
        state = Poll.load(f"tests/saved/{seed}")
        for key in ("users", "entities", "vouches", "public_settings", "ratings", "comparisons"):
            assert len(getattr(state, key)) > 0
