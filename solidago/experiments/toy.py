import sys
import json
import os
import logging
import numpy as np
import pandas as pd

from pathlib import Path

from solidago import *


dfs = TournesolExport.load_dfs("tests/tiny_tournesol.zip")
t = TournesolExport("tests/tiny_tournesol.zip")
            
with open("experiments/toy.json") as f: hps = json.load(f)
generative_model = GenerativeModel.load(hps["generative_model"])
    
state = State
generative_model.modules[0](state)
generative_model.modules[1](state)
generative_model.modules[2](state)
generative_model.modules[3](state)
generative_model.modules[4](state)
generative_model.modules[5](state)

# s = generative_model(30, 100, 2, 0)

# pipeline = Pipeline.from_json(hps["pipeline"])

# users, vouches, entities, privacy, judgments = synthetic_data
# users, voting_rights, user_models, global_model = pipeline(users_in, vouches, entities, privacy, judgments)

# t = tournesol_data.get_pipeline_kwargs(criterion="reliability")


