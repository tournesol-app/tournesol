
def test_user_models():
    from solidago import Entities, UserModels, Scores, Score, ScoringModel
    from solidago.poll.scoring.user_models import CommonMultipliers, CommonTranslations, \
        UserDirectScores, UserMultipliers, UserTranslations
    
    entities = Entities(dict(name=["entity_1", "entity_2", "entity_3"]))
    directs = UserModels(
        user_directs=UserDirectScores([
            ("aidjango", "entity_1", "default", 2, 1, 1),
            ("aidjango", "entity_1", "importance", 0, 1, 1),
            ("aidjango", "entity_2", "default", -1, 1, 1),
            ("aidjango", "entity_2", "importance", 3, 1, 10),
            ("aidjango", "entity_3", "default", 0, 0, 1),
            ("le_science4all", "entity_1", "default", 0, 0, 0),
            ("le_science4all", "entity_1", "importance", -3, 1, 1),
            ("le_science4all", "entity_2", "default", -1, 0, 1),
        ], columns=["username", "entity_name", "criterion", "value", "left_unc", "right_unc"])
    )
    assert directs.criteria() == {"default", "importance"}
    assert directs.get_composition("aidjango")[0] == ("Linear", dict())
    model = directs["aidjango"]
    assert isinstance(model, ScoringModel)

    scores = directs(entities)
    assert len(scores) == 10
    assert scores.get(username="le_science4all", entity_name="entity_1", criterion="default").to_triplet() == (0, 0, 0)

    user_multipliers = UserMultipliers([
        ("aidjango", "default", 2, 0.1, 1),
        ("aidjango", "importance", 1, 0, 0),
        ("le_science4all", "default", 1, 0, 0),
        ("le_science4all", "importance", 1, 0, 0),
    ], columns=["username", "criterion", "value", "left_unc", "right_unc"], keynames=["username", "criterion"])
    user_translations = UserTranslations([
            ("aidjango", "default", -1, 1, 1),
            ("aidjango", "importance", 0, 0, 0),
            ("le_science4all", "default", 1, 1, 1),
            ("le_science4all", "importance", 0, 0, 0),
        ], columns=["username", "criterion", "value", "left_unc", "right_unc"], keynames=["username", "criterion"])
    username = "aidjango"
    aidjango_directs_multipliers = directs.user_multipliers.filters(username=username)
    aidjango_multipliers = aidjango_directs_multipliers | user_multipliers.filters(username=username).add_keys(height=1)
    assert len(aidjango_multipliers) == 2
    assert aidjango_multipliers.get(criterion="default", height=1).value == 2

    scaled = directs.user_scale(user_multipliers, user_translations, note="second")
    _, scaled_model = next(iter(scaled))
    scores = scaled_model(entities)
    assert isinstance(scores, Scores)
    assert len(scores) > 0

    scores = scaled(entities)
    assert isinstance(scores, Scores)
    assert len(scores) == 10
    assert scores.get(username="le_science4all", entity_name="entity_1", criterion="default").value == 1.0
    assert scores.get(username="aidjango", entity_name="entity_3", criterion="default").left_unc == 1.0

    common_multipliers = CommonMultipliers([
        ("default", 2, 0, 0),
        ("importance", 1, 0, 1),
    ], columns=["criterion", "value", "left_unc", "right_unc"], keynames=["criterion"])
    common_translations = CommonTranslations([
        ("default", 1, 0, 0),
        ("importance", 3, 2, 2),
    ], columns=["criterion", "value", "left_unc", "right_unc"], keynames=["criterion"])
    rescaled = scaled.common_scale(common_multipliers, common_translations, note="third")
    multipliers = common_multipliers.add_columns(username=username)
    multipliers = multipliers.add_keys(height=len(scaled[username].composition))
    assert len(scaled[username].multipliers | multipliers) == 4
    rescaled_model = rescaled[username]
    scores = rescaled_model(entities)

    scores = rescaled(entities)
    assert isinstance(scores, Scores)
    assert len(scores) == 10
    assert scores.get(username="le_science4all", entity_name="entity_1", criterion="default").value == 3.0
    assert scores.get(username="aidjango", entity_name="entity_3", criterion="default").left_unc == 2.0

    squashed = rescaled.post_process("SquashProcessing", max=100.)
    scores = squashed(entities)
    assert isinstance(scores, Scores)    
    assert scores.get(username="le_science4all", entity_name="entity_1", criterion="importance").value == 0

    subscores = squashed(entities, "default")
    assert subscores.get(username="le_science4all", entity_name="entity_2").value > 70
    
    score = squashed["aidjango"](entities["entity_3"] , "importance")
    assert isinstance(score, Score)
    assert score.isnan()

    scores = squashed["aidjango"](entities["entity_2"])
    assert isinstance(scores, Scores)
    assert scores.get(criterion="importance") > 0
