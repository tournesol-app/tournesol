import pytest
from solidago import *


def test_voting_rights():
    voting_rights = VotingRights()
    voting_rights.set(0.5, "aidjango", "entity_4", "default")
    voting_rights.set(1., "le_science4all", "entity_4", "largely_recommended")
    assert voting_rights.get("aidjango", "entity_4", "default") == 0.5
    assert voting_rights.get("le_science4all", "entity_4", "largely_recommended") == 1
    assert voting_rights.get("le_science4all", "entity_4", "default") == 0
