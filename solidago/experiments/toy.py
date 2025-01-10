import sys
import json
import os
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from pandas import DataFrame, Series
from pathlib import Path
from numba import njit

from solidago import *
from solidago.primitives.optimize import coordinate_descent, njit_brentq


# t = TournesolExport("tests/tiny_tournesol.zip")

# generative_model = GenerativeModel.load("tests/generative_model/test_generative_model.json")
# s = generative_model()
# s.save("tests/pipeline/saved")

s = State.load("tests/pipeline/saved")
pipeline= Sequential.load("tests/pipeline/test_pipeline.json")

# s = pipeline(s, "tests/pipeline/saved")

# s = pipeline.trust_propagation.state2state_function(s, save_directory="tests/pipeline/saved")
# s = pipeline.preference_learning.state2state_function(s, save_directory="tests/pipeline/saved")
# s = pipeline.voting_rights.state2state_function(s, save_directory="tests/pipeline/saved")
# s = pipeline.scaling.state2state_function(s, save_directory="tests/pipeline/saved")
# s = pipeline.aggregation.state2state_function(s, save_directory="tests/pipeline/saved")
# s = pipeline.post_process.state2state_function(s, save_directory="tests/pipeline/saved")

self = NumbaUniformGBT()

assessments = s.assessments.reorder_keys(["username", "criterion", "entity_name"])
comparisons = s.comparisons.reorder_keys(["username", "criterion", "left_name", "right_name"])
user = next(iter(s.users))
assessments = assessments[user]
comparisons = comparisons[user]

compared_entity_names = comparisons.get_set("left_name") | comparisons.get_set("right_name")
entities = s.entities.get(compared_entity_names)
init = s.user_models[user](entities).reorder_keys(["criterion", "entity_name"])
comparisons = comparisons.reorder_keys(["criterion", "left_name", "right_name"])
criteria = comparisons.get_set("criterion") | init.get_set("criterion")
criterion = next(iter(criteria))
comparisons = comparisons[criterion]
init = init[criterion]

entity_name2index = { str(entity): index for index, entity in enumerate(entities) }
comparisons = comparisons.order_by_entities()

entity_index = np.random.randint(len(entities))
entity_name = entities.iloc[entity_index].name
scores = np.arange(len(entities), dtype=np.float64)

def get_partial_derivative_args(entity_index: int, scores: np.ndarray) -> tuple:
    entity_name = entities.iloc[entity_index].name
    normalized_comparisons = comparisons[entity_name].normalized_comparisons(self.last_comparison_only)
    df = comparisons[entity_name].to_df(last_row_only=self.last_comparison_only)
    indices = df["other_name"].map(entity_name2index)
    return scores[indices], np.array(normalized_comparisons)

get_partial_derivative_args(entity_index, scores)

empty_function = lambda coordinate, variable: tuple()
get_update_coordinate_function_args = empty_function

def coordinate_function(coordinate: int, variable: np.ndarray[np.float64]):
    @njit
    def f(value: np.float64, *partial_derivative_args) -> np.float64:
        return self.partial_derivative(coordinate, np.array([ 
            variable[i] if i != coordinate else value
            for i in range(len(variable))
        ], dtype=np.float64), *partial_derivative_args)
    return f

coordinate_optimization_xtol = 1e-5
def update_coordinate_function(coordinate: int, variable: np.ndarray[np.float64], *coordinate_update_args) -> float:
    return njit_brentq(
        f=coordinate_function(coordinate, variable),
        args=get_partial_derivative_args(coordinate, variable, *coordinate_update_args),
        xtol=coordinate_optimization_xtol,
        a=variable[coordinate] - 1.0,
        b=variable[coordinate] + 1.0
    )
