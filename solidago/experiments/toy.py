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

with open("tests/generative_model/test_generative_model.json") as f: 
    generative_model = GenerativeModel.load(json.load(f))
s = generative_model(seed=0)

# s = State.load("tests/pipeline/saved")
with open("tests/pipeline/test_pipeline.json") as f: 
    pipeline= Sequential.load(json.load(f))

# r = pipeline(s, "tests/pipeline/saved")

s = pipeline.trust_propagation.state2state_function(s, save_directory="tests/pipeline/saved")
s = pipeline.preference_learning.state2state_function(s, save_directory="tests/pipeline/saved")
s = pipeline.voting_rights.state2state_function(s, save_directory="tests/pipeline/saved")
s = pipeline.scaling.state2state_function(s, save_directory="tests/pipeline/saved")
# r = pipeline.aggregation.state2state_function(s, save_directory="tests/pipeline/saved")
# r = pipeline.post_process.state2state_function(s, save_directory="tests/pipeline/saved")
