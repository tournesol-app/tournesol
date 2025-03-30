import timeit
import logging.config
logging.config.fileConfig('experiments/info.conf')

logger = logging.getLogger(__name__)

start = timeit.default_timer()
logger.info("Loading packages and modules")

import sys, json, os, timeit
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pandas import DataFrame, Series

import solidago
from solidago import *
from solidago.primitives.datastructure import *
from solidago.primitives.lipschitz import *
from solidago.primitives.optimize import *

# generator = Generator.load("tests/generators/test_generator.json")
# pipeline = Sequential.load("tests/modules/test_pipeline.json")
pipeline = Sequential.load("src/solidago/modules/tournesol_full.json")
end = timeit.default_timer()
logger.info(f"Loaded packages in {int(end - start)} seconds")


##################################################################
##########             Loading input states             ##########
##################################################################

start = timeit.default_timer()
logger.info("Loading input states")
# states = [ State.load(f"tests/saved/{seed}") for seed in range(5) ]
# processed_states = [ pipeline(states[seed], f"tests/saved/{seed}") for seed in range(5) ]
# s = State.load("tests/saved/0")
# s = generator(seed=0)
# s = TournesolExport("tests/tiny_tournesol.zip")
# dfs = TournesolExport.load_dfs("experiments/tournesol.zip")
s = TournesolExport("experiments/tournesol.zip")

# users, entities, vouches, made_public = s.users, s.entities, s.vouches, s.made_public
# assessments, comparisons, voting_rights = s.assessments, s.comparisons, s.voting_rights
# user_models, global_model = s.user_models, s.global_model
end = timeit.default_timer()
logger.info(f"Loaded states in {int(end - start)} seconds")


##################################################################
##########             Process the states               ##########
##################################################################

start = timeit.default_timer()
print("Running the pipeline")
t = pipeline(s, "experiments/tournesol_processed")

# s1 = pipeline.trust_propagation.state2state_function(s)
# s2 = pipeline.preference_learning.state2state_function(s1)
# s3 = pipeline.voting_rights.state2state_function(s2)
# s4 = pipeline.scaling.state2state_function(s3)
# s5 = pipeline.aggregation.state2state_function(s4)
# s6 = pipeline.post_process.state2state_function(s5)
end = timeit.default_timer()
print(f"Pipeline terminated in {int(end - start)} seconds")
