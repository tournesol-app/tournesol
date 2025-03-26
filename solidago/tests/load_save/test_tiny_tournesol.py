import pytest
from solidago import *

def test_import():
    t = TournesolExport("tests/tiny_tournesol.zip")
    
    assert "biscuissec" in t.users, t.users
    assert t.users.loc["le_science4all", "trust_score"] == 1
    assert "NatNgs" in set(t.vouches["aidjango"].keys("to"))
    assert t.vouches["aidjango", "biscuissec", "Personhood"] == (1, 0)
    assert "aBdymwisfb4" in t.entities
    assert isinstance(t.made_public, AllPublic)
    assert len(t.assessments) == 0
    assert len(t.comparisons) == 2268
    assert len(t.comparisons["amatissart"]) == 19
    assert t.comparisons.get(entity_name="Tt5AwEU_BiM").keys("username") == {'amatissart', 'biscuissec', 'white'}
    assert t.comparisons.get_evaluators("N8G-KGqn2Lg") == {'amatissart'}
    assert t.voting_rights["Tit0uan", "xMxo9pIC0GA", "largely_recommended"] == 0.86
    assert len(t.voting_rights["Tit0uan"]) == 3
    assert "lpfaucon" in t.user_models
    assert len(t.user_models["lafabriquesociale"]) == 3
    assert len(t.voting_rights["lpfaucon"]) == len(t.user_models["lpfaucon"])
    assert t.user_models["lpfaucon"]("YVxJNhR9U4g", "largely_recommended").value == 93.18
    assert t.global_model("0BoRX6UrBv0")["importance"].to_triplet() == (-4.53, 141.1, 141.1)

def test_export():
    t = TournesolExport("tests/tiny_tournesol.zip")
    t.user_models.scale(
        MultiScore(["username", "kind", "criterion"], {
            (username, "multiplier", "largely_recommended"): Score(2, 0, 0)
            for username, model in t.user_models
        } | {
            (username, "translation", "importance"): Score(3, 0, 0)
            for username, model in t.user_models
        }, note="user_scale_test_export")
    )
    t.user_models.scale(
        MultiScore(["kind", "criterion"], {
            ("translation", "importance"): Score(2, 0, 0)
        }, note="common_scale_test_export")
    )
    t.save("tests/load_save/save_tiny_tournesol")

def test_reimport():
    t = State.load("tests/load_save/save_tiny_tournesol")
    
    assert "biscuissec" in t.users, t.users
    assert t.users.loc["le_science4all", "trust_score"] == 1
    assert "NatNgs" in set(t.vouches["aidjango"].keys("to"))
    assert t.vouches["aidjango", "biscuissec", "Personhood"] == (1, 0)
    assert "aBdymwisfb4" in t.entities
    assert isinstance(t.made_public, AllPublic)
    assert len(t.assessments) == 0
    assert len(t.comparisons) == 2268
    assert len(t.comparisons["amatissart"]) == 19
    assert t.comparisons.get(entity_name="Tt5AwEU_BiM").keys("username") == {'amatissart', 'biscuissec', 'white'}
    assert t.comparisons.get_evaluators("N8G-KGqn2Lg") == {'amatissart'}
    assert t.voting_rights["Tit0uan", "xMxo9pIC0GA", "largely_recommended"] == 0.86
    assert len(t.voting_rights["Tit0uan"]) == 3
    assert "lpfaucon" in t.user_models
    assert len(t.user_models["lafabriquesociale"].parent.parent) == 3
    assert len(t.voting_rights["lpfaucon"]) == len(t.user_models["lpfaucon"].parent.parent)
    assert t.user_models["lpfaucon"]("YVxJNhR9U4g", "largely_recommended").value == 186.36
    assert t.global_model("0BoRX6UrBv0")["importance"].to_triplet() == (-4.53, 141.1, 141.1)

