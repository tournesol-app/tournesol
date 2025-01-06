import sys
import json
import os
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from pandas import DataFrame, Series
from pathlib import Path

from solidago import *


# t = TournesolExport("tests/tiny_tournesol.zip")

# with open("tests/generative_model/test_generative_model.json") as f: 
    # generative_model = GenerativeModel.load(json.load(f))
# s = generative_model(seed=0)

with open("tests/pipeline/test_pipeline.json") as f: 
    pipeline= Sequential.load(json.load(f))

s = State.load("tests/tmp")
r = pipeline(s, "tests/tmp")

# r1 = pipeline.trust_propagation.state2state_function(s, save_directory="tests/pipeline")
# r2 = pipeline.preference_learning.state2state_function(r1, save_directory="tests/pipeline")
# r3 = pipeline.voting_rights.state2state_function(r2, save_directory="tests/pipeline")
# r4 = pipeline.scaling.state2state_function(r3, save_directory="tests/pipeline")
# r5 = pipeline.aggregation.state2state_function(r4)
# r6 = pipeline.post_process.state2state_function(r5)

# r = pipeline(s)

# users, vouches, entities, privacy, judgments = synthetic_data
# users, voting_rights, user_models, global_model = pipeline(users_in, vouches, entities, privacy, judgments)

# t = tournesol_data.get_pipeline_kwargs(criterion="reliability")


