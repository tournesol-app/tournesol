import pandas as pd

from tournesol.models import Poll


def apply_poll_scaling_on_global_scores(poll: Poll, global_scores: pd.DataFrame):
    # Apply poll scaling
    scale_function = poll.scale_function
    global_scores["uncertainty"] = 0.5 * (
        scale_function(global_scores["score"] + global_scores["uncertainty"])
        - scale_function(global_scores["score"] - global_scores["uncertainty"])
    )
    global_scores["deviation"] = 0.5 * (
        scale_function(global_scores["score"] + global_scores["deviation"])
        - scale_function(global_scores["score"] - global_scores["deviation"])
    )
    global_scores["score"] = scale_function(global_scores["score"])


def apply_poll_scaling_on_individual_scaled_scores(
    poll: Poll, scaled_scores: pd.DataFrame
):
    scale_function = poll.scale_function
    scaled_scores["uncertainty"] = 0.5 * (
        scale_function(scaled_scores["score"] + scaled_scores["uncertainty"])
        - scale_function(scaled_scores["score"] - scaled_scores["uncertainty"])
    )
    scaled_scores["score"] = scale_function(scaled_scores["score"])
