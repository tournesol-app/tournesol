def test_score():
    from solidago import Score
    
    assert Score(1) + Score(1) == Score(2)
    assert Score((1, 1, 0)) + Score((1, 0, 1)) == Score((2, 1, 1))
    assert (Score((1, 1, 0)) * Score((1, 0, 1))).max == 2
    assert Score((1, 1, 1)) < Score((3, 0, 2))
    assert Score((1, 1, 2)) >= Score((3, 0, 2))
    assert not (Score((1, 1, 2)) <= Score((-3, 0, 2)))
    assert not Score((-3, 0, 2)).abs().contains(4)

def test_scores():
    from solidago import Scores, Score

    s = Scores(keynames=["criterion"])
    s.set(criterion="default", value=1, left_unc=4, right_unc=2)
    s.set(criterion="importance", value=2, left_unc=1, right_unc=0)
    s.set(criterion="fun", value=1, left_unc=0, right_unc=2)
    assert s.get(criterion="fun") == Score((1, 0, 2))
    assert s.get(criterion="fun") == Score((1, 0, 2))
    assert s.get(criterion="fun") + s.get(criterion="importance") == Score((3, 1, 2))
    assert s.get(criterion="diversity").isnan()
    
    t = Scores(keynames=["criterion"])
    t.set(criterion="default", value=1)
    p = s * t
    assert isinstance(p, Scores)
    assert p.get(criterion="default") == s.get(criterion="default")
    assert p.get(criterion="importance").isnan()
    assert p.get(criterion="default").average_uncertainty() == 3
    
    u = Scores(keynames=["entity_name", "criterion"])
    u.set(criterion="default", entity_name="entity_1", value=1)
    q = s + u
    assert isinstance(q, Scores)
    assert set(q.keynames) == {"entity_name", "criterion"}
    assert q.get(criterion="default", entity_name="entity_1") == Score((2, 4, 2))

    z = u + s
    assert isinstance(z, Scores)
    assert set(z.keynames) == {"entity_name", "criterion"}
    assert z.get(criterion="default", entity_name="entity_1") == Score((2, 4, 2))


def test_direct():
    from solidago import ScoringModel, Entity, Entities, Scores, Score
    from solidago.poll import Multipliers, Translations, Linear

    direct = ScoringModel()
    entities = Entities(dict(name=["entity_1", "entity_2"]))
    direct.directs.set(entity_name="entity_1", criterion="default", value=1, left_unc=5, right_unc=2)
    direct.directs.set(entity_name="entity_2", criterion="default", value=2, left_unc=3, right_unc=1)
    direct.directs.set(entity_name="entity_2", criterion="importance", value=2, left_unc=0, right_unc=1)
    assert direct.evaluated_entity_names() == {"entity_1", "entity_2"}
    entities = direct.sample_entities(entities, {"default", "importance"})
    assert isinstance(entities, Entities)
    assert len(entities) == 2
    base_scoring = direct.base_scoring
    assert isinstance(base_scoring, Linear)
    scores = Scores(keynames=["entity_name", "criterion"], default_score=(0., 0., 0.))
    scores2 = base_scoring.direct_scoring(entities, None)
    assert isinstance(scores2, Scores)
    assert len(scores2) == 3

    scores = direct(entities)
    assert isinstance(scores, Scores)
    assert len(scores) == 3
    
    multipliers, translations = Multipliers(keynames=["criterion"]), Translations(keynames=["criterion"])
    multipliers.set(criterion="default", value=1)
    multipliers.set(criterion="importance", value=2, left_unc=1, right_unc=1)
    translations.set(criterion="default", value=1)
    translations.set(criterion="importance", value=3, left_unc=2, right_unc=0)
    scaled = direct.scale(multipliers, translations)

    nonscaled_scores = scaled.base_score(entities, {"default", "importance"})
    assert isinstance(nonscaled_scores, Scores)
    assert len(nonscaled_scores) == 3
    assert nonscaled_scores.get(entity_name="entity_1", criterion="default") == scores.get(entity_name="entity_1", criterion="default")
    
    scores = scaled(entities)
    assert isinstance(scores, Scores)
    assert scores.get(entity_name="entity_1", criterion="default") == Score((2, 5, 2))

    squashed = scaled.post_process("SquashProcessing", max=100)
    scores = squashed(entities)
    assert isinstance(scores, Scores)
    assert scores.get(entity_name="entity_1", criterion="importance").isnan()
    assert scores.get(entity_name="entity_2", criterion="importance").value > 98
    assert scores.get(entity_name="entity_2", criterion="importance").value < 100
    assert len(scores) == 3

    assert scores.get(entity_name="entity_2", criterion="importance").value == squashed(Entity("entity_2"), "importance").value
