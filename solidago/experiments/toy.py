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

# from tests.generate_test_states import *
# save_generated_data()

# states = [ State.load(f"tests/modules/saved/{seed}") for seed in range(5) ]
# states = [ pipeline(s, f"tests/modules/saved/{seed}", skip_steps={2, 3, 4, 5}) for seed in range(5) ]

s = State.load("tests/saved/0")
# s = generator(seed=0)

# s1 = pipeline.trust_propagation.state2state_function(s)
# s2 = pipeline.preference_learning.state2state_function(s1)
# s3 = pipeline.voting_rights.state2state_function(s2)
# s4 = pipeline.scaling.state2state_function(s3)
# s5 = pipeline.aggregation.state2state_function(s4)
# s6 = pipeline.post_process.state2state_function(s5)

# t = pipeline(s)

# users, entities, made_public, user_models = s.users, s.entities, s.made_public, s.user_models
# criterion = next(iter(user_models.criteria()))
# scores = user_models(entities, criterion)
# trusts = dict(zip(users.index, users["trust_score"]))

# self = pipeline.scaling.collaborative_scaling
# activities, is_scaler = self.compute_activities_and_scalers(users, trusts, made_public, scores)
# users[f"activities_{criterion}"] = activities
# users[f"is_scaler_{criterion}"] = is_scaler
# scalers = users.get({ f"is_scaler_{criterion}": True })

# scaler_scales, scaler_scores = self.scale_to_scalers(trusts, made_public, scores[scalers], scores[scalers], scalees_are_scalers=True)
# scalee_model_norms = self.compute_model_norms(made_public, scalee_scores)
        
# for seed in range(5):
    # directory = f"tests/modules/saved/{seed}"
    # pipeline(State.load(directory), directory, skip_steps={3, 4, 5})

# tiny = TournesolExport("tests/tiny_tournesol.zip")

# t = TournesolExport("experiments/tournesol.zip")
# t = State.load("experiments/saved_tournesol")
# pipeline = solidago.Sequential.load("tests/pipeline/test_pipeline.json")

# r = pipeline(t)

