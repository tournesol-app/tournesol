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
    
# s = generative_model()

# pipeline = Pipeline.from_json(hps["pipeline"])

# users, vouches, entities, privacy, judgments = synthetic_data
# users, voting_rights, user_models, global_model = pipeline(users_in, vouches, entities, privacy, judgments)

# t = tournesol_data.get_pipeline_kwargs(criterion="reliability")


