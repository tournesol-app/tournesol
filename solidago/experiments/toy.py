import sys
import json
import os
import logging.config
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

logging.config.fileConfig('experiments/info.conf')

from pandas import DataFrame, Series
from pathlib import Path
from numba import njit

from solidago import *
from solidago.primitives.datastructure import *
from solidago.primitives.lipschitz import *
from solidago.primitives.optimize import *


generator = Generator.load("tests/generators/test_generator.json")
pipeline = Sequential.load("tests/modules/test_pipeline.json")

# states = [ State.load(f"tests/saved/{seed}") for seed in range(5) ]
# processed_states = [ pipeline(states[seed], f"tests/saved/{seed}") for seed in range(5) ]

# s = State.load("tests/saved/0")
# s = generator(seed=0)

s = TournesolExport("tests/tiny_tournesol.zip")

# s1 = pipeline.trust_propagation.state2state_function(s)
# s2 = pipeline.preference_learning.state2state_function(s1)
# s3 = pipeline.voting_rights.state2state_function(s2)
# s4 = pipeline.scaling.state2state_function(s3)
# s5 = pipeline.aggregation.state2state_function(s4)
# s6 = pipeline.post_process.state2state_function(s5)

# users, entities, made_public, user_models = s.users, s.entities, s.made_public, s.user_models
# criterion = "default"
# scores = user_models(entities, criterion)
# trusts = dict(zip(users.index, users["trust_score"]))
# self = pipeline.scaling.collaborative_scaling

# activities, is_scaler = self.compute_activities_and_scalers(users, trusts, made_public, scores)
# users[f"activities_{criterion}"] = activities
# users[f"is_scaler_{criterion}"] = is_scaler
# scalers = users.get({ f"is_scaler_{criterion}": True })

# scaler_scales, scaler_scores = self.scale_to_scalers(trusts, made_public, 
    # scores.get_all(scalers), scores.get_all(scalers), scalees_are_scalers=True)

# nonscalers = users.get({ f"is_scaler_{criterion}": False })
# nonscaler_scores = scores.get_all(nonscalers)
# scalee_scores = nonscaler_scores
# scalee_model_norms = self.compute_model_norms(made_public, scalee_scores)

# key_names = ["scalee_name", "scaler_name"]
# weight_lists = VotingRights(key_names=key_names, last_only=False)
# comparison_lists = MultiScore(key_names=key_names, last_only=False)

# scalee_name = next(iter(set(scalee_scores["username"])))
# scalee_name_scores = scalee_scores.get(username=scalee_name, cache_groups=True)
# scalee_entity_names = set(scalee_name_scores["entity_name"])

# scaler_names = set.union(*[
	# set(scaler_scores.get(entity_name=entity_name, cache_groups=True)["username"])
	# for entity_name in scalee_entity_names
# ])
            
# t = pipeline(s)
        
# for seed in range(5):
    # directory = f"tests/modules/saved/{seed}"
    # pipeline(State.load(directory), directory, skip_steps={3, 4, 5})

# tiny = TournesolExport("tests/tiny_tournesol.zip")

# t = TournesolExport("experiments/tournesol.zip")
# t = State.load("experiments/saved_tournesol")
# pipeline = solidago.Sequential.load("tests/pipeline/test_pipeline.json")

# r = pipeline(t)

