from solidago.pipeline.inputs import TournesolDataset
from solidago.privacy_settings import PrivacySettings

def test_privacy_io():
    privacy = PrivacySettings()
    privacy[2, 5] = False
    privacy[1, 3] = True
    assert not privacy[2, 5]
    assert privacy[1, 3]
    assert privacy[0, 2] is None

def test_tournesol_import():
    inputs = TournesolDataset("tests/data/tiny_tournesol.zip")
    privacy = inputs.get_pipeline_kwargs(criterion="largely_recommended")["privacy"]
    aidjango_id = inputs.users[inputs.users["public_username"] == "aidjango"].index[0]
    video_id_to_entity_id = {
        video_id: entity_id
        for (entity_id, video_id) in inputs.entity_id_to_video_id.items()
    }
    assert privacy[aidjango_id, video_id_to_entity_id['dBap_Lp-0oc']] == False
