from solidago import *


def test_public_settings():
    public_settings = PublicSettings()
    public_settings.set(username="aidjango", entity_name="entity_4", public=False)
    public_settings.set(username="le_science4all", entity_name="entity_4", public=True)
    assert not public_settings.get(username="aidjango", entity_name="entity_4")["public"]
    assert public_settings.get(username="le_science4all", entity_name="entity_4")["public"]
