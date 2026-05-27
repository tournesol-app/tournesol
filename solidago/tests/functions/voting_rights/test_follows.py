from solidago import *
poll = Poll.load("tests/test_poll")

from solidago.functions.voting_rights import Follows
f = Follows(follow_lifetime=10, username="charlie", date=100)
users, socials = poll.users, poll.socials
voting_rights = f.fn(users, socials)

def test_follows():
    assert set(voting_rights("username")) == {"hank", "dave", "alice", "bob"}
    assert all((voting_rights("follow_volume") - [0.0368392 , 0.02134472, 0.02722941, 0.02722941])**2 < 1e-3)