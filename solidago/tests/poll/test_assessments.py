from solidago import *


def test_ratings():
    ratings = Ratings()
    ratings["user_0", "default", "entity_4"] = Rating(5)
    ratings["user_5", "default", "entity_3"] = Rating(5, 0, 10)
    ratings["user_5", "default", "entity_3"] = Rating(value=2, min=0, max=10)
    assert ratings["user_2", "default", "entity_4"] is None
    for (username, criterion, entity_name), rating in ratings:
        assert isinstance(rating, Rating)
    assert ratings.get_evaluators("entity_3") == {"user_5"}
    assert len(ratings) == 2
    assert ratings["user_5", "default", "entity_3"].value == 2
