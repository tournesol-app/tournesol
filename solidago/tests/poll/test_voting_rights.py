from solidago import *


def test_voting_rights():
    voting_rights = VotingRights()
    voting_rights.set(username="aidjango", entity_name="entity_4", criterion="default", voting_right=0.5)
    voting_rights.set(username="le_science4all", entity_name="entity_4", criterion="largely_recommended", voting_right=1)
    assert voting_rights.get(username="aidjango", entity_name="entity_4", criterion="default")["voting_right"] == 0.5
    assert voting_rights.get(username="le_science4all", entity_name="entity_4", criterion="largely_recommended")["voting_right"] == 1
    assert voting_rights.get(username="le_science4all", entity_name="entity_4", criterion="default")["voting_right"] == 0
