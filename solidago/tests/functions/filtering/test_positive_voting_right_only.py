from solidago import *
poll = Poll.load("tests/test_poll")

def test_positive_voting_right_only_alice():
    username = "alice"
    from solidago.primitives.time import Date
    from solidago.functions import Sequential
    from solidago.functions.filtering import RemoveRecommendedEntities, PositiveVotingRightOnly
    from solidago.functions.voting_rights import Follows, Mentions, AggregateVolumes
    f = Sequential([RemoveRecommendedEntities(), Follows(), Mentions(), AggregateVolumes(),PositiveVotingRightOnly()])
    f.customize(username, Date(100))
    p = f(poll)
    assert set(p.users.names()) == {"alice", "bob", "charlie", "dave", "erin", "felix", "grace", "hank"}
    assert all(
        p.voting_rights.get(username=u.name)["voting_right"] > 0 
        for u in p.users if u.name != username
    )

def test_positive_voting_right_only_bob():
    username = "bob"
    from solidago.primitives.time import Date
    from solidago.functions import Sequential
    from solidago.functions.filtering import RemoveRecommendedEntities, PositiveVotingRightOnly
    from solidago.functions.voting_rights import Follows, Mentions, AggregateVolumes
    f = Sequential([RemoveRecommendedEntities(), Follows(), Mentions(), AggregateVolumes(),PositiveVotingRightOnly()])
    f.customize(username, Date(100))
    p = f(poll)
    assert set(p.users.names()) == {"alice", "bob", "erin", "felix", "hank"}
    assert all(
        p.voting_rights.get(username=u.name)["voting_right"] > 0 
        for u in p.users if u.name != username
    )