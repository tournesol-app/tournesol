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
s.save("tests/pipeline/saved")

s = State.load("tests/pipeline/saved")
with open("tests/pipeline/test_pipeline.json") as f: 
    pipeline= Sequential.load(json.load(f))

# r = pipeline(s, "tests/pipeline/saved")

r1 = pipeline.trust_propagation.state2state_function(s, save_directory="tests/pipeline/saved")
r2 = pipeline.preference_learning.state2state_function(r1, save_directory="tests/pipeline/saved")
r3 = pipeline.voting_rights.state2state_function(r2, save_directory="tests/pipeline/saved")
r4 = pipeline.scaling.state2state_function(r3, save_directory="tests/pipeline/saved")
# r5 = pipeline.aggregation.state2state_function(r4, save_directory="tests/pipeline/saved")
# r6 = pipeline.post_process.state2state_function(r5, save_directory="tests/pipeline/saved")
