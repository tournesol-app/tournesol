import pytest
from importlib import import_module
from solidago.pipeline import Pipeline
from solidago.pipeline.inputs import TournesolInputFromPublicDataset


@pytest.mark.parametrize("test", range(5))
def test_pipeline_test_data(test):
    td = import_module(f"data.data_{test}")
    Pipeline()(td.users, td.vouches, td.entities, td.privacy, td.judgments)


def test_tournesol_get_comparisons():
    dataset = TournesolInputFromPublicDataset("tests/data/tiny_tournesol.zip")

    # Test no filter
    assert len(dataset.get_comparisons()) == 38387

    # Test single filter
    assert len(dataset.get_comparisons(
            criteria="importance"
        )) == 17143
    assert len(dataset.get_comparisons(
            user_id=dataset.username_to_user_id["le_science4all"]
        )) == 5604

    # Test all filters
    assert len(dataset.get_comparisons(
            criteria="largely_recommended",
            user_id=dataset.username_to_user_id["lpfaucon"]
        )) == 8471


def test_tournesol_get_individual_scores():
    dataset = TournesolInputFromPublicDataset("tests/data/tiny_tournesol.zip")

    # Test no filter
    assert len(dataset.get_individual_scores()) == 17319

    # Test single filter
    assert len(dataset.get_individual_scores(
            criteria="largely_recommended"
        )) == 9176
    assert len(dataset.get_individual_scores(
            user_id=dataset.username_to_user_id["aidjango"]
        )) == 4379
    assert len(dataset.get_individual_scores(
            entity_id=dataset.video_id_to_entity_id["dBap_Lp-0oc"]
        )) == 5

    # Test multiple filters
    assert len(dataset.get_individual_scores(
            criteria="importance",
            user_id=dataset.username_to_user_id["biscuissec"]
        )) == 1493
    assert len(dataset.get_individual_scores(
            criteria="largely_recommended",
            entity_id=dataset.video_id_to_entity_id["zItOqgnSvi8"]
        )) == 2
    assert len(dataset.get_individual_scores(
            user_id=dataset.username_to_user_id["amatissart"],
            entity_id=dataset.video_id_to_entity_id["BTUVUg9RQSg"]
        )) == 1

    # Test all filters
    user_id = dataset.username_to_user_id["le_science4all"]
    entity_id = dataset.video_id_to_entity_id["03dTJ4nXkXw"]
    found = dataset.get_individual_scores(
        criteria="importance",
        user_id=user_id,
        entity_id=entity_id
    )
    assert len(found) == 1
    as_dict = found.to_dict(orient="records")[0]
    assert as_dict == {
        'user_id': user_id,
        'entity_id': entity_id,
        'criteria': 'importance',
        'score': 82.81,
        'uncertainty': 24.37,
        'voting_right': 1.0,
        'comparisons': 10,
    }


def test_tournesol_get_collective_scores():
    dataset = TournesolInputFromPublicDataset("tests/data/tiny_tournesol.zip")

    # Test no filter
    assert len(dataset.get_collective_scores()) == 12184

    # Test single filter
    assert len(dataset.get_collective_scores(
            criteria="largely_recommended"
        )) == 6227
    assert len(dataset.get_collective_scores(
            entity_id=dataset.video_id_to_entity_id["kX3JKg-H5qM"]
        )) == 2

    # Test all filters
    entity_id = dataset.video_id_to_entity_id["OlhC6n9Hhac"]
    found = dataset.get_collective_scores(
        criteria="importance",
        entity_id=entity_id
    )
    assert len(found) == 1
    as_dict = found.to_dict(orient="records")[0]
    assert as_dict == {
        'entity_id': entity_id,
        'criteria': 'importance',
        'score': 18.22,
        'uncertainty': 60.09,
        'users': 3,
        'comparisons': 12,
    }
