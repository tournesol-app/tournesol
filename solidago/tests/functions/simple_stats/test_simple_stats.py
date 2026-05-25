from solidago import *
from solidago.poll.scoring.user_models import *

poll = Poll.load("tests/test_poll")

def test_post_actions_learning():
    p = functions.simple_stats.UserStats(max_workers=1)(poll)
    p = functions.simple_stats.EntityStats(max_workers=1)(p)
    p = functions.simple_stats.ComparisonStats("main", {"main", "reliability", "importance"}, max_workers=1)(p)
    users, entities, comparisons = p.users, p.entities, p.comparisons

    assert set(users.columns) == {'trustworthy', 'pretrust',
        'n_ratings', 'n_comparisons', 'n_evaluated_entities',
        'n_repost_ratings', 'n_repost_comparisons', 'n_repost_evaluated_entities',
        'n_reliability_ratings', 'n_reliability_comparisons', 'n_reliability_evaluated_entities',
        'n_importance_ratings', 'n_importance_comparisons', 'n_importance_evaluated_entities',
        'n_report_ratings', 'n_report_comparisons', 'n_report_evaluated_entities',
        'n_main_ratings', 'n_main_comparisons', 'n_main_evaluated_entities'}
    assert users["grace"]["n_ratings"] == 3
    assert users["grace"]["n_repost_ratings"] == 2
    assert users["grace"]["n_evaluated_entities"] == 3
    assert users["erin"]["n_comparisons"] == 9
    assert users["erin"]["n_main_comparisons"] == 8
    assert users["erin"]["n_repost_comparisons"] == 0
    assert users["erin"]["n_evaluated_entities"] == 9

    assert set(entities.columns) == {'authors', 'mentions', 'timestamp',
        'n_comparers', 'n_comparisons', 'n_evaluators', 'n_raters', 'n_ratings'}
    assert entities["banana"]["authors"] == ("alice", "bob")
    assert entities["banana"]["mentions"] == ("charlie",)
    assert entities["banana"]["n_comparers"] == 1
    assert entities["coconut"]["n_comparers"] == 2
    assert entities["coconut"]["n_comparisons"] == 4
    assert entities["coconut"]["n_evaluators"] == 4
    assert entities["durian"]["n_raters"] == 3
    assert entities["durian"]["n_ratings"] == 4

    assert set(comparisons.columns) == {
        'username', 'criterion', 'left_name', 'right_name', 'timestamp', 'value', 'max',
        'multiple_criteria', 'all_criteria', 
        'first_value', 'left_first', 'right_first', 
        'user_trust'}
    assert all(comparisons("user_trust") == 1)
    assert not all(comparisons.filters(username="erin", left_name="apple", right_name="banana")("all_criteria"))
    assert not all(comparisons.filters(username="erin", left_name="banana", right_name="coconut")("all_criteria"))
    assert all(comparisons.filters(username="erin", left_name="apple", right_name="banana")("multiple_criteria"))
    assert not all(comparisons.filters(username="erin", left_name="banana", right_name="coconut")("multiple_criteria"))
    assert np.isnan(comparisons("first_value")[0])
    assert comparisons("first_value")[1] == 1
    assert comparisons("first_value")[2] == 3
    assert np.isnan(comparisons("first_value")[3])
    assert np.isnan(comparisons("first_value")[4])
    assert comparisons("first_value")[5] == 0
    assert comparisons("first_value")[6] == 3
    assert all(comparisons("left_first")[:5] == [True, True, False, True, False])
    assert all(comparisons("right_first")[:5] == [True, False, True, True, False])
