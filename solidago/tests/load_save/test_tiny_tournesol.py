import pytest
from solidago import *

def test_import():
    t = TournesolExport("tests/tiny_tournesol.zip")
    
    assert "biscuissec" in t.users, t.users
    assert t.users.loc["le_science4all", "trust_score"] == 1
    assert "NatNgs" in set(t.vouches.get("aidjango")["to"])
    assert t.vouches.get("aidjango", "biscuissec", "Personhood") == (1, 0)
    assert "aBdymwisfb4" in t.entities
    assert isinstance(t.made_public, AllPublic)
    assert len(t.assessments) == 0
    assert len(t.comparisons) == 2268
    assert len(t.comparisons["amatissart"]) == 19
    assert t.comparisons[any, any, "Tt5AwEU_BiM", any].get_set("username") == {'amatissart', 'biscuissec'}
    assert t.comparisons.get_evaluators("N8G-KGqn2Lg") == {'amatissart'}
    assert t.voting_rights.get("Tit0uan", "xMxo9pIC0GA", "largely_recommended") == 0.86
    assert len(t.voting_rights.get("Tit0uan")) == 3
    assert "lpfaucon" in t.user_models
    assert len(t.user_models["lafabriquesociale"].to_df()) == 3
    assert len(t.voting_rights.get("lpfaucon")) == len(t.user_models["lpfaucon"].to_df())
    assert t.user_models["lpfaucon"]("YVxJNhR9U4g")["largely_recommended"].value == 93.18
    assert t.global_model("0BoRX6UrBv0")["importance"].to_triplet() == (-4.53, 141.1, 141.1)

def test_export():
    t = TournesolExport("tests/tiny_tournesol.zip")
    t.user_models = UserModels({
        username: ScaledModel(model, ScaleDict({
            "largely_recommended": (2, 0, 0, 0, 0, 0),
            "importance": (1, 0, 0, 5, 0, 0),
        })) for username, model in t.user_models
    })
    t.save("tests/load_save/save_tiny_tournesol")

def test_reimport():
    t = State.load("tests/load_save/save_tiny_tournesol")
    
    assert "biscuissec" in t.users, t.users
    assert t.users.loc["le_science4all", "trust_score"] == 1
    assert "NatNgs" in set(t.vouches.get("aidjango")["to"])
    assert t.vouches.get("aidjango", "biscuissec", "Personhood") == (1, 0)
    assert isinstance(t.made_public, AllPublic)
    assert len(t.assessments) == 0
    assert len(t.comparisons) == 2268
    assert len(t.comparisons["amatissart"]) == 19
    assert t.comparisons[any, any, "Tt5AwEU_BiM", any].get_set("username") == {'amatissart', 'biscuissec'}
    assert t.comparisons.get_evaluators("N8G-KGqn2Lg") == {'amatissart'}
    assert t.voting_rights.get("Tit0uan", "xMxo9pIC0GA", "largely_recommended") == 0.86
    assert len(t.voting_rights.get("Tit0uan")) == 3
    assert "lpfaucon" in t.user_models
    assert len(t.user_models["lafabriquesociale"].to_dfs()["directs"]) == 3
    assert len(t.voting_rights.get("lpfaucon")) == len(t.user_models["lpfaucon"].to_dfs()["directs"])
    assert t.user_models["lpfaucon"]("YVxJNhR9U4g")["largely_recommended"].value == 186.36
    assert t.global_model("0BoRX6UrBv0")["importance"].to_triplet() == (-4.53, 141.1, 141.1)
