from typing import Optional

import pandas as pd

from solidago.pipeline import TournesolInput
from .parameters import PipelineParameters


def get_individual_scores(
    input: TournesolInput,
    criteria: str,
    parameters: PipelineParameters,
    single_user_id: Optional[int] = None,
) -> pd.DataFrame:
    comparisons_df = input.get_comparisons(criteria=criteria, user_id=single_user_id)
    # Legacy pipeline assumes all comparisons use the same 'score_max'
    score_max_series = comparisons_df.pop("score_max")
    if score_max_series.nunique() > 1:
        raise RuntimeError(
            "Legacy pipeline does not support multiple 'score_max' in comparisons. "
            f"Found {dict(score_max_series.value_counts())}"
        )

    initial_contributor_scores = input.get_individual_scores(
        criteria=criteria, user_id=single_user_id
    )
    if initial_contributor_scores is not None:
        initial_contributor_scores = initial_contributor_scores.groupby("user_id")

    individual_scores = []
    for user_id, user_comparisons in comparisons_df.groupby("user_id"):
        if initial_contributor_scores is None:
            initial_entity_scores = None
        else:
            try:
                contributor_score_df = initial_contributor_scores.get_group(user_id)
                initial_entity_scores = pd.Series(
                    data=contributor_score_df.raw_score, index=contributor_score_df.entity
                )
            except KeyError:
                initial_entity_scores = None
        scores = parameters.indiv_algo.compute_individual_scores(
            user_comparisons, initial_entity_scores=initial_entity_scores
        )
        if scores is None:
            continue
        scores["user_id"] = user_id
        individual_scores.append(scores.reset_index())

    if len(individual_scores) == 0:
        return pd.DataFrame(columns=["user_id", "entity_id", "raw_score", "raw_uncertainty"])

    result = pd.concat(individual_scores, ignore_index=True, copy=False)
    return result.reindex(columns=["user_id", "entity_id", "raw_score", "raw_uncertainty"])
