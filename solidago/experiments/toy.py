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


# generative_model = GenerativeModel.load("tests/generative_model/test_generative_model.json")
# states = [ State.load(f"tests/pipeline/saved/{seed}") for seed in range(5) ]
# tiny = TournesolExport("tests/tiny_tournesol.zip")

t = TournesolExport("experiments/tournesol.zip")
pipeline= Sequential.load("tests/pipeline/test_pipeline.json")

print("Tournesol data loaded. Now running the pipeline.")
r = pipeline(t, save_directory="experiments/saved_tournesol")

# self = pipeline.preference_learning

# username = "aunyx"
# user = t.users.get(username)
# entities = t.entities
# comparisons = t.comparisons[user]
# init_model = t.user_models[user]

# compared_entity_names = comparisons.get_set("left_name") | comparisons.get_set("right_name")
# entities = entities.get(compared_entity_names) # Restrict to compared entities
# init = init_model(entities).reorder_keys(["criterion", "entity_name"])
# comparisons = comparisons.reorder_keys(["criterion", "left_name", "right_name"])
# criteria = comparisons.get_set("criterion") | init.get_set("criterion")

# criterion = next(iter(criteria))
# self.user_learn_criterion(entities, comparisons[criterion], init[criterion])
