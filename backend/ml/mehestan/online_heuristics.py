import numpy as np
import pandas as pd
from ml.inputs import MlInput
from tournesol.models.entity_score import ScoreMode
from ml.outputs import (
    save_contributor_scores,
    save_entity_scores,
    save_tournesol_score_as_sum_of_criteria,
)


R_MAX = 10  # Maximum score for a comparison in the input
ALPHA = 0.01  # Signal-to-noise hyperparameter

def apply_online_update_on_individual_score(all_comparison_user: pd.DataFrame,uid_a: str, uid_b : str, previous_individual_raw_scores: pd.DataFrame):
    scores = all_comparison_user[["entity_a", "entity_b", "score"]]
    if (uid_a,uid_b) not in { twotuple_entity_id for (twotuple_entity_id, _) in scores.groupby(["entity_a","entity_b"])}  \
    and \
    (uid_b,uid_a) not in { twotuple_entity_id for (twotuple_entity_id, _) in scores.groupby(["entity_a","entity_b"])}:
        return 

    scores_sym = pd.concat(
        [
            scores,
            pd.DataFrame(
                {
                    "entity_a": scores.entity_b,
                    "entity_b": scores.entity_a,
                    "score": -1 * scores.score,
                }
            ),
        ]
    )

    # "Comparison tensor": matrix with all comparisons, values in [-R_MAX, R_MAX]
    r = scores_sym.pivot(index="entity_a", columns="entity_b", values="score")

    r_tilde = r / (1.0 + R_MAX)
    r_tilde2 = r_tilde ** 2

    # r.loc[a:b] is negative when a is prefered to b.
    l = -1.0 * r_tilde / np.sqrt(1.0 - r_tilde2)  # noqa: E741
    k = (1.0 - r_tilde2) ** 3

    L = k.mul(l).sum(axis=1)
 

    Kaa_np=np.array(k.sum(axis=1) + ALPHA)

    L_tilde=L/Kaa_np
    L_tilde_a=L_tilde[uid_a]
    L_tilde_b=L_tilde[uid_b]

    U_ab=-k/Kaa_np[:,None]
    U_ab=U_ab.fillna(0)

    


    theta_star_a = L_tilde_a - (U_ab*previous_individual_raw_scores)[uid_a]
    theta_star_b = L_tilde_b - (U_ab*previous_individual_raw_scores)[uid_b]

    previous_individual_raw_scores[uid_a]=theta_star_a
    previous_individual_raw_scores[uid_b]=theta_star_b


def run_online_heuristics(ml_input: MlInput, uid_a: str, uid_b:str, user_id:str,criteria :str, poll:Poll):
    all_comparison_user=ml_input.get_comparisons(criteria = criteria,user_id = user_id)
    previous_individual_raw_scores=ml_input.get_scores(user_id)
    apply_online_update_on_individual_score(all_comparison_user,uid_a,uid_b, previous_individual_raw_scores)
    save_contributor_scores(poll, previous_individual_raw_scores, single_criteria=criteria)
    s,tau=ml_input.get_scaling_factors(user_id)
    previous_individual_raw_scores=s*previous_individual_raw_scores+tau
    for mode in ScoreMode:
        global_scores = get_global_scores(scaled_scores, score_mode=mode)
        global_scores["criteria"] = criteria
        save_entity_scores(poll, global_scores, single_criteria=criteria, score_mode=mode)

    save_tournesol_score_as_sum_of_criteria(poll)    