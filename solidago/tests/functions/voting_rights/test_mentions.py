import pytest
from solidago import *
poll = Poll.load("tests/test_poll")
users, entities, socials = poll.users, poll.entities, poll.socials

def test_follows():
    from solidago.functions.voting_rights import Follows, Mentions
    voting_rights = Follows(follow_lifetime=10, username="alice", date=100).fn(users, socials)
    followed_follow_volumes = voting_rights("follow_volume")
    mention_volume, relative_max_volume = .5, .2
    voting_rights = Mentions(mention_volume=.5, relative_max_volume=.2, username="alice", date=100)\
        .fn(users, entities, voting_rights)
    assert voting_rights("mention_volume").sum() <= relative_max_volume * followed_follow_volumes.sum()
    assert voting_rights.keys("username") == {"bob", "charlie", "dave", "erin", "felix", "grace", "hank"}
    squared_followed_mention_volumes = voting_rights\
        .filters(username={"bob", "charlie", "dave", "felix", "grace"})("mention_volume")**2
    assert all(squared_followed_mention_volumes < 1e-6)
    nonfollowed_mention_volumes = voting_rights.filters(username={"erin", "hank"})("mention_volume")
    assert all(nonfollowed_mention_volumes <= mention_volume)

@pytest.mark.parametrize("username", users.names())
def test_all_follows(username):
    from solidago.functions.voting_rights import Follows, Mentions
    voting_rights = Follows(follow_lifetime=10, username=username, date=100).fn(users, socials)
    total_follow_volumes = voting_rights("follow_volume").sum()
    mention_volume, relative_max_volume = .5, .2
    voting_rights = Mentions(mention_volume=.5, relative_max_volume=.2, username=username, date=100)\
        .fn(users, entities, voting_rights)
    nonfollowed_mention_volumes = voting_rights("mention_volume")
    max_total_mention_volumes = relative_max_volume * total_follow_volumes
    assert voting_rights("mention_volume").sum() <= max_total_mention_volumes
    assert all(nonfollowed_mention_volumes <= mention_volume)
    assert all(voting_rights("mention_volume") == 0)\
        or (voting_rights("mention_volume").sum() >= max_total_mention_volumes - 1e-6)\
        or all(nonfollowed_mention_volumes >= mention_volume - 1e-6)