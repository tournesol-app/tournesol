import pytest
from solidago import *


def test_assessments():
    assessments = Assessments()
    assessments.add_row("user_0", "default", "entity_4", value=5)
    assessments.add_row("user_5", "default", "entity_3", value=5, max=10)
    assert assessments.get("user_2", "default", "entity_4") is None
    for (username, criterion, entity_name), assessment in assessments:
        assert isinstance(assessment, Assessment)
    assert assessments.get_evaluators("entity_3") == {"user_5"}
    
