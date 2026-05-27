import pytest
from solidago import *
poll = Poll.load("tests/test_poll")
users, entities, socials = poll.users, poll.entities, poll.socials

@pytest.mark.parametrize("username", users.names())
def test_all_follows(username):
    from solidago.functions.voting_rights import Follows, Mentions, AggregateVolumes
    voting_rights = Follows(follow_lifetime=10, username=username, date=100).fn(users, socials)
    voting_rights = Mentions(username=username, date=100).fn(users, entities, voting_rights)
    voting_rights = AggregateVolumes().fn(voting_rights)
    left = voting_rights("follow_volume") + voting_rights("mention_volume")
    right = voting_rights("voting_right")
    assert all((left - right)**2 < 1e-6)