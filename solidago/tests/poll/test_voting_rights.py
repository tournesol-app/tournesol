import pytest
from solidago import *


def test_voting_rights():
    voting_rights = VotingRights()
    voting_rights["aidjango", "entity_4", "default"] = 0.5
    voting_rights["le_science4all", "entity_4", "largely_recommended"] = 1
    assert voting_rights["aidjango", "entity_4", "default"] == 0.5
    assert voting_rights["le_science4all", "entity_4", "largely_recommended"] == 1
    assert voting_rights["le_science4all", "entity_4", "default"] == 0
