import numpy as np
from solidago import *


def test_ratings():
    ratings = Ratings()
    ratings.set(username="user_0", criterion="default", entity_name="entity_4", value=5)
    ratings.set(username="user_5", criterion="default", entity_name="entity_3", value=5, min=0, max=10)
    ratings.set(username="user_5", criterion="default", entity_name="entity_3", value=2, min=0, max=10)
    assert np.isnan(ratings.get(username="user_2", criterion="default", entity_name="entity_4")["value"])
    for rating in ratings:
        assert isinstance(rating, Rating)
    assert ratings.filters(entity_name="entity_3").keys("username") == {"user_5"}
    assert len(ratings) == 3
    assert len(ratings.filters(username="user_5")) == 2
    assert ratings.get(username="user_5", criterion="default", entity_name="entity_3")["value"] == 2
