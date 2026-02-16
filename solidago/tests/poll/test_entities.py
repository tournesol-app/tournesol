import numpy as np
from solidago.poll.poll_tables import Entity, Entities


def test_entity():
    entity = Entity("video_a", vector=[1., 2.], n_views=315)
    assert all(entity.vector == np.array([1., 2.]))
    assert entity["n_views"] == 315


def test_entities():
    entities = Entities([
        ["video_a", 155, 0, 1, 2],
        ["video_b", 83, 3., 4, 5],
    ], columns=["name", "n_views", "v0", "v1", "v2"])
    assert len(entities) == 2
    assert entities["video_a"]["n_views"] == 155
    assert len(entities[["video_a"]]) == 1 # type: ignore
    assert all(entities["video_b"].vector == entities.vectors[1]) # type: ignore
