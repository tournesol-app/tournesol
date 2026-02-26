def test_import():
    import pytest
    from solidago import TournesolExport, PublicSettings, Scores

    t = TournesolExport("tests/tiny_tournesol.zip")
    
    assert "biscuissec" in t.users, t.users
    assert t.users["le_science4all"]["trust"] == 1
    assert "NatNgs" in set(t.vouches.filters(by="aidjango").keys("to"))
    assert t.vouches.get(by="aidjango", to="biscuissec", kind="Personhood")["weight"] == 1
    assert t.vouches.get(by="aidjango", to="biscuissec", kind="Personhood")["priority"] == 0
    assert "aBdymwisfb4" in t.entities
    assert isinstance(t.public_settings, PublicSettings)
    assert len(t.ratings) == 0
    assert len(t.comparisons) == 2268
    assert len(t.comparisons.filters(username="amatissart")) == 19
    assert t.comparisons.filters(left_name="Tt5AwEU_BiM").keys("username") | \
        t.comparisons.filters(right_name="Tt5AwEU_BiM").keys("username") == {'amatissart', 'biscuissec', 'white'}
    assert t.comparisons.filters(left_name="N8G-KGqn2Lg").keys("username") | \
        t.comparisons.filters(right_name="N8G-KGqn2Lg").keys("username") == {'amatissart'}
    assert t.voting_rights.get(username="Tit0uan", entity_name="xMxo9pIC0GA", criterion="largely_recommended")["voting_right"] == 0.86
    assert len(t.voting_rights.filters(username="Tit0uan")) == 3
    assert "lpfaucon" in t.user_models
    scores = t.user_models["lafabriquesociale"](t.entities)
    assert isinstance(scores, Scores)
    assert len(scores) == 3
    scores = t.user_models["lpfaucon"](t.entities)
    assert isinstance(scores, Scores)
    assert len(t.voting_rights.filters(username="lpfaucon")) == len(scores)
    assert t.user_models["lpfaucon"](t.entities["YVxJNhR9U4g"], "largely_recommended").value == pytest.approx(2.5671393153744293)
    scores = t.global_model(t.entities["0BoRX6UrBv0"])
    assert isinstance(scores, Scores)
    assert scores.get(criterion="importance").to_triplet() == pytest.approx((-4.53, 141.1, 141.1))

def test_export():
    from solidago import TournesolExport
    from solidago.poll.scoring.user_models import CommonMultipliers, UserMultipliers, UserTranslations

    t = TournesolExport("tests/tiny_tournesol.zip")
    t.user_models = t.user_models.user_scale(
        UserMultipliers([
            (username, "largely_recommended", 2, 0, 0)
            for username, _ in t.user_models
        ], columns=["username", "criterion", "value", "left_unc", "right_unc"], keynames=["username", "criterion"]),
        UserTranslations([
            (username, "importance", 3, 0, 0)
            for username, _ in t.user_models
        ], columns=["username", "criterion", "value", "left_unc", "right_unc"], keynames=["username", "criterion"]),
        note="user_scale_test_export"
    )
    t.user_models = t.user_models.common_scale(
        CommonMultipliers([("importance", 2, 0, 0)], columns=["criterion", "value", "left_unc", "right_unc"], keynames=["criterion"]),
        note="common_scale_test_export"
    )
    t.save("tests/load_save/save_tiny_tournesol")

def test_reimport():
    import pytest
    from solidago import PublicSettings, Scores, Poll

    t = Poll.load("tests/load_save/save_tiny_tournesol")
    assert "biscuissec" in t.users, t.users
    assert t.users["le_science4all"]["trust"] == 1
    assert "NatNgs" in set(t.vouches.filters(by="aidjango").keys("to"))
    assert t.vouches.get(by="aidjango", to="biscuissec", kind="Personhood")["weight"] == 1
    assert t.vouches.get(by="aidjango", to="biscuissec", kind="Personhood")["priority"] == 0
    assert "aBdymwisfb4" in t.entities
    assert isinstance(t.public_settings, PublicSettings)
    assert len(t.ratings) == 0
    assert len(t.comparisons) == 2268
    assert len(t.comparisons.filters(username="amatissart")) == 19
    assert t.comparisons.filters(left_name="Tt5AwEU_BiM").keys("username") | \
        t.comparisons.filters(right_name="Tt5AwEU_BiM").keys("username") == {'amatissart', 'biscuissec', 'white'}
    assert t.comparisons.filters(left_name="N8G-KGqn2Lg").keys("username") | \
        t.comparisons.filters(right_name="N8G-KGqn2Lg").keys("username") == {'amatissart'}
    assert t.voting_rights.get(username="Tit0uan", entity_name="xMxo9pIC0GA", criterion="largely_recommended")["voting_right"] == 0.86
    assert len(t.voting_rights.filters(username="Tit0uan")) == 3
    assert "lpfaucon" in t.user_models
    scores = t.user_models["lafabriquesociale"](t.entities)
    assert isinstance(scores, Scores)
    assert len(scores) == 3
    scores = t.user_models["lpfaucon"](t.entities)
    assert isinstance(scores, Scores)
    assert len(t.voting_rights.filters(username="lpfaucon")) == len(scores)
    assert t.user_models["lpfaucon"](t.entities["YVxJNhR9U4g"], "largely_recommended").value == pytest.approx(2 * 2.5671393153744293)
    scores = t.global_model(t.entities["0BoRX6UrBv0"])
    assert isinstance(scores, Scores)
    assert scores.get(criterion="importance").to_triplet() == pytest.approx((-4.53, 141.1, 141.1))

