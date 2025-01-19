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
# t = State.load("experiments/saved_tournesol")
pipeline = Sequential.load("tests/pipeline/test_pipeline.json")


self = pipeline.preference_learning

user = t.users.get("aidjango")
criterion = "importance"
comparisons = t.comparisons[user, criterion]
init = t.user_models[user].base_model()[0]
init = init.reorder_keys(["criterion", "entity_name"])[criterion]
entity_names = comparisons.get_set("left_name") | comparisons.get_set("right_name")
entities = t.entities.get(entity_names)

entity_name2index = { str(entity): index for index, entity in enumerate(entities) }
scores = self.init_scores(entity_name2index, init)
loss = self.negative_log_posterior(scores, entities, entity_name2index, comparisons)
loss.backward()

nans = { i for i in range(len(scores)) if scores.grad[i].isnan() }
comparison_dict = comparisons.to_comparison_dict(entities, True)

# r = pipeline.voting_rights.state2state_function(r)

# print("Tournesol data loaded. Now running the pipeline.")
# r = pipeline(t)
