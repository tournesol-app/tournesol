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

from solidago.modules.preference_learning import NumbaUniformGBT, LBFGSUniformGBT

s = State.load(f"tests/saved/0")
user_models = dict()
for optimizer in (NumbaUniformGBT, LBFGSUniformGBT):
    preference_learning = optimizer(
        prior_std_dev=7.0,
        uncertainty_nll_increase=1.0,
        max_uncertainty=1e3,
        last_comparison_only=True,
    )
    user_models[optimizer.__name__] = preference_learning.state2objects_function(s)
