from solidago import *

poll = Poll.load("tests/test_poll")


def test_filtering():
    p = functions.filtering.Filtering(criteria="repost").fn(poll)
    assert len(p.users) == 8
    assert len(p.entities) == 10
    assert len(p.socials) == 36
    assert len(p.ratings) == 14

    p = functions.filtering.Filtering(usernames=["grace", "hank"], criteria="repost").fn(poll)
    assert len(p.users) == 2
    assert len(p.entities) == 10
    assert len(p.socials) == 4
    assert len(p.ratings) == 3

    p = functions.filtering.Filtering(usernames=["grace", "hank"], entity_names=["apple"], criteria="repost").fn(poll)
    assert len(p.users) == 2
    assert len(p.entities) == 1
    assert len(p.socials) == 4
    assert len(p.ratings) == 2
    
    p = functions.filtering.Filtering(criteria="main").fn(poll)
    assert len(p.socials) == 36
    assert len(p.ratings) == 16