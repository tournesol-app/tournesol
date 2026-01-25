from solidago import *


def test_assessments():
    assessments = Assessments()
    assessments["user_0", "default", "entity_4"] = Assessment(5)
    assessments["user_5", "default", "entity_3"] = Assessment(5, 0, 10)
    assessments["user_5", "default", "entity_3"] = Assessment(value=2, min=0, max=10)
    assert assessments["user_2", "default", "entity_4"] is None
    for (username, criterion, entity_name), assessment in assessments:
        assert isinstance(assessment, Assessment)
    assert assessments.get_evaluators("entity_3") == {"user_5"}
    assert len(assessments) == 2
    assert assessments["user_5", "default", "entity_3"].value == 2
