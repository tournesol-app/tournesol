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

# s = State.load("tests/saved/0")
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

# init = MultiScore("entity_name")
# GBT.get_partial_derivative_args(entities, comparisons)

# from solidago.modules.preference_learning import NumbaUniformGBT, LBFGSUniformGBT
# import torch

s = State.load(f"tests/saved/0")
# entities = s.entities
# comparisons = s.comparisons["user_0", "default"]
# prior_std_dev = 7.0
# kwargs = dict(prior_std_dev=prior_std_dev, uncertainty_nll_increase=1.0, max_uncertainty=1e3)

# left_indices, right_indices = comparisons.left_right_indices(entities)
# normalized_comparisons = torch.tensor(comparisons.normalized_comparison_list())
# negative_log_posterior_args = left_indices, right_indices, normalized_comparisons
# indices = comparisons.compared_entity_indices(entities) # defaultdict[int, list]
# indices = [ indices[i] for i in range(len(entities)) ]
# entity_normalized_comparisons = comparisons.entity_normalized_comparisons(entities) # defaultdict
# entity_normalized_comparisons = [ np.array(entity_normalized_comparisons[i]) for i in range(len(entities)) ]

# GBTs = [GBT(**kwargs) for GBT in (NumbaUniformGBT, LBFGSUniformGBT)]
# user_models = [gbt.state2objects_function(s) for gbt in GBTs]
# values = [GBTs[0].init_values(entities, um["user_0"](entities, "default")) for um in user_models]
# numbaGradients = [GBTs[0].gradient(v, entities, comparisons) for v in values]
# lbfgsGradients = list()
# for i in range(2):
    # v = torch.tensor(values[i])
    # v.requires_grad = True
    # l = GBTs[1].negative_log_posterior(v, left_indices, right_indices, normalized_comparisons)
    # l.backward()
    # lbfgsGradients.append(v.grad.detach())

# numbaPriorGradients = [v / prior_std_dev**2 for v in values]
# lbfgsPriorGradients = list()
# for i in range(2):
    # v = torch.tensor(values[i])
    # v.requires_grad = True
    # l = (v**2).sum() / (2 * prior_std_dev**2)
    # l.backward()
    # lbfgsPriorGradients.append(v.grad.detach())
