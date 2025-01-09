import pytest
from solidago import *


def test_assessments():
    assessments = Assessments()
    assessments["user_0", "default", "entity_4"] = [ dict(assessement=5) ]
    assessments.add_row(["user_5", "default", "entity_3"], dict(assessement=5, assessement_max=10))
    assert assessments["user_2", "default", "entity_4"] == list()
    for (username, criterion, entity_name), assessment in assessments:
        assert isinstance(assessment, Assessment)
    assert assessments.get_evaluators("entity_3") == {"user_5"}
    assert "user_5" in assessments.reorder_keys(["entity_name", "username", "criterion"])["entity_3"]
    
