import pytest
import importlib

from solidago.aggregation import Aggregation, StandardizedQrMedian, Average
from solidago.scoring_model import ScaledScoringModel

from solidago.aggregation.standardized_qr_quantile import _get_user_scores


@pytest.mark.parametrize( "test", list(range(5)) )
def test_aggregation(test):
    """ Basic run of pipelines on test data """
    td = importlib.import_module(f"data.data_{test}")
    user_models, global_model = td.pipeline.aggregation(
        td.voting_rights,
        td.standardized_models,
        td.users,
        td.entities
    )

@pytest.mark.parametrize( "test", list(range(1, 5)) )
def test_qtlstd(test):
    """ The output of StandardizedQrMedian should be independent from
    the multiplicative scales of input user models, as long as it is the same for all users.
    """
    td = importlib.import_module(f"data.data_{test}")
    df = _get_user_scores(td.voting_rights, td.standardized_models, td.entities)
    aggregation = StandardizedQrMedian(dev_quantile=0.9, lipschitz=1e20, error=1e-6)
    std_dev = aggregation._compute_std_dev(df)
    scaled_models = { 
        u: ScaledScoringModel(base_model=td.standardized_models[u], multiplicator=2)
        for u in td.standardized_models
    }
    df2 = _get_user_scores(td.voting_rights, scaled_models, td.entities)
    std_dev2 = aggregation._compute_std_dev(df2)
    assert 2 * std_dev == pytest.approx(std_dev2, abs=1e-4)

@pytest.mark.parametrize( "test", list(range(5)) )
def test_qtlstd_qrmed_invariance(test):
    """ The output of StandardizedQrMedian should be independent from
    the multiplicative scales of input user models, as long as it is the same for all users.
    """
    td = importlib.import_module(f"data.data_{test}")
    aggregation = StandardizedQrMedian(dev_quantile=0.9, lipschitz=10000., error=1e-7)
    user_models, global_model = aggregation(
        td.voting_rights,
        td.standardized_models,
        td.users,
        td.entities
    )
    user_models2, global_model2 = aggregation(
        td.voting_rights,
        { 
            u: ScaledScoringModel(base_model=td.standardized_models[u], multiplicator=2)
            for u in td.standardized_models
        },
        td.users,
        td.entities
    )
    for u in user_models:
        for e in user_models[u].scored_entities(td.entities):
            score = user_models[u](e, td.entities.loc[e])
            score2 = user_models2[u](e, td.entities.loc[e])
            assert score == pytest.approx(score2, abs=1e-2)
    
    for e in global_model.scored_entities(td.entities):
        score = global_model(e, td.entities.loc[e])
        score2 = global_model2(e, td.entities.loc[e])
        assert score == pytest.approx(score2, abs=1e-2)
    

@pytest.mark.parametrize( "test", list(range(5)) )
def test_average(test):
    td = importlib.import_module(f"data.data_{test}")
    aggregation = Average()
    user_models, global_model = aggregation(
        td.voting_rights,
        td.standardized_models,
        td.users,
        td.entities
    )
    user_models2, global_model2 = aggregation(
        td.voting_rights,
        { 
            u: ScaledScoringModel(base_model=td.standardized_models[u], multiplicator=2)
            for u in td.standardized_models
        },
        td.users,
        td.entities
    )
    for u in user_models:
        for e in user_models[u].scored_entities(td.entities):
            score = user_models[u](e, td.entities.loc[e])
            score2 = td.standardized_models[u](e, td.entities.loc[e])
            assert score == pytest.approx(score2, abs=1e-2)
    
    for e in global_model.scored_entities(td.entities):
        score = global_model(e, td.entities.loc[e])
        score2 = global_model2(e, td.entities.loc[e])
        for i in range(3):
            assert 2 * score[i] == pytest.approx(score2[i], abs=1e-2)
    
