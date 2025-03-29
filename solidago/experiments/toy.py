import sys
import json
import os
import logging.config
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import timeit

logging.config.fileConfig('experiments/info.conf')

from pandas import DataFrame, Series
from pathlib import Path
from numba import njit

import solidago
from solidago import *
from solidago.primitives.datastructure import *
from solidago.primitives.lipschitz import *
from solidago.primitives.optimize import *


# generator = Generator.load("tests/generators/test_generator.json")
# pipeline = Sequential.load("tests/modules/test_pipeline.json")

# states = [ State.load(f"tests/saved/{seed}") for seed in range(5) ]
# processed_states = [ pipeline(states[seed], f"tests/saved/{seed}") for seed in range(5) ]

s = State.load("tests/saved/0")
# s = generator(seed=0)
# s = TournesolExport("tests/tiny_tournesol.zip")
# s = TournesolExport("experiments/tournesol.zip")

# t = pipeline(s)

# s1 = pipeline.trust_propagation.state2state_function(s)
# s2 = pipeline.preference_learning.state2state_function(s1)
# s3 = pipeline.voting_rights.state2state_function(s2)
# s4 = pipeline.scaling.state2state_function(s3)
# s5 = pipeline.aggregation.state2state_function(s4)
# s6 = pipeline.post_process.state2state_function(s5)

users, entities, vouches, made_public = s.users, s.entities, s.vouches, s.made_public
assessments, comparisons, voting_rights = s.assessments, s.comparisons, s.voting_rights
user_models, global_model = s.user_models, s.global_model

self = solidago.modules.scaling.Mehestan(
    lipschitz=1., 
    min_scaler_activity=1.,
    n_scalers_max=5, 
    privacy_penalty=0.5,
    user_comparison_lipschitz=10.,
    p_norm_for_multiplicative_resilience=4.0,
    n_entity_to_fully_compare_max=100,
    error=1e-5
)

scales = MultiScore(keynames=["username", "kind", "criterion"])
for criterion in user_models.criteria():
    scores = user_models(entities, criterion)
    output = self.scale_criterion(users, entities, made_public, scores)
    subscales, activities, is_scaler = output
    scales |= subscales.prepend(criterion=criterion)
    users[f"activities_{criterion}"] = activities
    users[f"is_scaler_{criterion}"] = is_scaler
        
# criterion = next(iter(user_models.criteria()))
# scores = user_models(entities, criterion)
# activities, is_scaler = self.compute_activities_and_scalers(users, made_public, scores)
# scalers, nonscalers = set(), set()
# for index, user in enumerate(users):
    # (scalers if is_scaler[index] else nonscalers).add(str(user))
# scaler_scores, nonscaler_scores = scores[scalers], scores[nonscalers]
# scalee_scores, scalees_are_scalers = scaler_scores, True

# scalee_model_norms = self.compute_model_norms(made_public, scalee_scores)
# ratio_weight_lists, ratio_lists = self.ratios(made_public, scaler_scores, scalee_scores)
# ratio_args = users, ratio_weight_lists, ratio_lists, self.default_multiplier_dev
# voting_rights, ratios = self.aggregate_scaler_scores(*ratio_args)
# multipliers = self.compute_multipliers(voting_rights, ratios, scalee_model_norms)

# for (scalee_name, entity_name), score in scalee_scores:
    # scalee_scores[scalee_name, entity_name] = score * multipliers[scalee_name]
# if scalees_are_scalers:
    # scaler_scores = scalee_scores

# diff_weight_lists, diff_lists = self.diffs(made_public, scaler_scores, scalee_scores)
# diff_args = users, diff_weight_lists, diff_lists, self.default_translation_dev
# voting_rights, diffs = self.aggregate_scaler_scores(*diff_args)
# translations = self.compute_translations(voting_rights, diffs)

# for (scalee_name, entity_name), score in scalee_scores:
    # scalee_scores[scalee_name, entity_name] = score + translations[scalee_name]

# multipliers = multipliers.prepend(kind="multiplier")
# translations = translations.prepend(kind="translation")
# scalee_scales = (multipliers | translations).reoroder("username", "kind")
