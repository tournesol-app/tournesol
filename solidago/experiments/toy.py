import sys
import json
import os
import logging
import numpy as np
import pandas as pd

from pandas import DataFrame, Series
from pathlib import Path

from solidago import *


# t = TournesolExport("tests/tiny_tournesol.zip")

with open("tests/generative_model/test_generative_model.json") as f: 
    generative_model = GenerativeModel.load(json.load(f))
s = generative_model(seed=0)

with open("tests/pipeline/test_pipeline.json") as f: 
    pipeline= Sequential.load(json.load(f))

r = pipeline(s)

# users, vouches, entities, privacy, judgments = synthetic_data
# users, voting_rights, user_models, global_model = pipeline(users_in, vouches, entities, privacy, judgments)

# t = tournesol_data.get_pipeline_kwargs(criterion="reliability")


