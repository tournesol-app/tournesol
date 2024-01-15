from solidago.generative_model.entity_model import SvdEntityModel

def test_svd_entity_model():
    entity_model = SvdEntityModel(svd_dimension=5)
    entities = entity_model(n_entities=100)
    assert len(entities) == 100
