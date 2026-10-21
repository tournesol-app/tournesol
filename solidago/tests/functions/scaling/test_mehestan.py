from solidago import *
from solidago.poll.scoring import *


users = Users(["user_0", "user_1"])
entities = Entities(["entity_0", "entity_1", "entity_2", "entity_3"])
public_settings = PublicSettings()
user_models = UserModels(
    user_directs=UserDirectScores([
        ("user_0", "entity_0", "default", 2, 1, .5),
        ("user_0", "entity_1", "default", 1, .2, .1),
        ("user_0", "entity_3", "default", .2, .4, .3),
        ("user_1", "entity_0", "default", -1.2, 1, .5),
        ("user_1", "entity_2", "default", -.3, .2, .1),
        ("user_1", "entity_3", "default", .4, .4, .3),
    ], columns=["username", "entity_name", "criterion", "value", "left_unc", "right_unc"])
)


def test_mehestan():
    mehestan = functions.scaling.Mehestan(max_workers=1)
    scaled_users, scaled = mehestan.fn(users, entities, public_settings, user_models)
    assert len(scaled_users) == len(users)
    assert len(user_models) == len(scaled)


reference_scores = {"entity_0": -1.5, "entity_1": -0.5, "entity_2": 0.5, "entity_3": 1.5}


def scores_of_three_users(transform_last_user_score) -> Scores:
    rows = [
        (username, entity_name, "default", score, .1, .1)
        for username in ("user_0", "user_1")
        for entity_name, score in reference_scores.items()
    ] + [
        ("user_2", entity_name, "default", transform_last_user_score(score), .1, .1)
        for entity_name, score in reference_scores.items()
    ]
    columns = ["username", "entity_name", "criterion", "value", "left_unc", "right_unc"]
    user_models = UserModels(user_directs=UserDirectScores(rows, columns=columns))
    return user_models(Entities(list(reference_scores))).filters(criterion="default")


def scale_three_users(transform_last_user_score):
    mehestan = functions.scaling.Mehestan(lipschitz=1., min_scaler_activity=1., max_workers=1)
    three_users = Users(["user_0", "user_1", "user_2"])
    scores = scores_of_three_users(transform_last_user_score)
    multipliers, translations, _, _ = mehestan.scale_criterion(
        three_users, Entities(list(reference_scores)), PublicSettings(), scores
    )
    return multipliers, translations


def test_mehestan_computes_a_multiplier_and_a_translation_per_user():
    multipliers, translations = scale_three_users(lambda score: score)
    assert len(multipliers) == 3
    assert len(translations) == 3


def test_mehestan_shrinks_the_scores_of_a_user_with_larger_scores():
    multipliers, _ = scale_three_users(lambda score: 2 * score)
    assert multipliers.get(username="user_2").value < 1
    assert multipliers.get(username="user_0").value >= 1


def test_mehestan_shifts_the_scores_of_a_user_with_higher_scores_down():
    _, translations = scale_three_users(lambda score: score + 2)
    assert translations.get(username="user_2").value < 0
    assert translations.get(username="user_0").value >= 0