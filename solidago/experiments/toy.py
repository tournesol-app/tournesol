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
# s = TournesolExport("experiments/tournesol.zip")

users, entities = s.users, s.entities
vouches, made_public = s.vouches, s.made_public
assessments, comparisons = s.assessments, s.comparisons
voting_rights = s.voting_rights
user_models, global_models = s.user_models, s.global_model

start = timeit.default_timer()
for user in users:
    model = DirectScoring()
    user_entities = entities.get(compared_entity_names) # Restrict to compared entities
    compared_entity_names = set(comparisons["left_name"]) | set(comparisons["right_name"])
    init = init_model(user_entities).to_dict("criterion")
    criteria = set(comparisons["criterion"]) | set(init["criterion"])
    for criterion, cmps in comparisons.to_dict("criterion"):
        criterion_entity_names = set(cmps["left_name"]) | set(cmps["right_name"])
        if len(criterion_entity_names) <= 1:
            continue
        criterion_entities = entities.get(criterion_entity_names) # Restrict to compared entities
        learned_scores = self.user_learn_criterion(criterion_entities, cmps, init[criterion])
        for entity_name, score in learned_scores:
            if not score.isnan():
                model.set(entity_name, criterion, score)
stop = timeit.default_timer()
print(f"Terminated in {round(stop - start, 2)} seconds")

# t = pipeline(s)

# s1 = pipeline.trust_propagation.state2state_function(s)
# s2 = pipeline.preference_learning.state2state_function(s1)
# s3 = pipeline.voting_rights.state2state_function(s2)
# s4 = pipeline.scaling.state2state_function(s3)
# s5 = pipeline.aggregation.state2state_function(s4)
# s6 = pipeline.post_process.state2state_function(s5)

# user = s.users.get("A")
# entities = s.entities
# assessments = s.assessments.get(user)
# comparisons = s.comparisons.get(user)
# init_model = s.user_models[user].base_model()

# # self = pipeline.preference_learning
# self = modules.preference_learning.NumbaUniformGBT()
# # self.user_learn(user, entities, assessments, comparisons, init_model)
# if self.last_comparison_only:
	# comparisons = comparisons.last_only()
# model = DirectScoring()
# compared_entity_names = set(comparisons["left_name"]) | set(comparisons["right_name"])
# entities = entities.get(compared_entity_names) # Restrict to compared entities
# init = init_model(entities).to_dict("criterion")
# criteria = set(comparisons["criterion"]) | set(init["criterion"])
# criterion = next(iter(criteria))
# cmps = comparisons.get(criterion=criterion)
# criterion_entity_names = set(cmps["left_name"]) | set(cmps["right_name"])
# if len(criterion_entity_names) > 1:
	# criterion_entities = entities.get(criterion_entity_names) # Restrict to compared entities
	# learned_scores = self.user_learn_criterion(criterion_entities, cmps, init[criterion])

