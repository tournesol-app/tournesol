from solidago import *
poll = Poll.load("tests/test_poll")

def test_remove_recommended_entities():
    username = "alice"
    from solidago.functions.filtering import RemoveRecommendedEntities
    p = RemoveRecommendedEntities(50, 2, username, 100)(poll)
    assert len(p.entities.names()) == 8
    assert "durian" not in p.entities
    assert "jackfruit" not in p.entities
    assert "durian" not in p.ratings("entity_name")