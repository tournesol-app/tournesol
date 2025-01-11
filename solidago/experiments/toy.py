import sys
import json
import os
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from pandas import DataFrame, Series
from pathlib import Path
from numba import njit

from solidago import *
from solidago.primitives.datastructure import *
from solidago.primitives.lipschitz import *


# t = TournesolExport("tests/tiny_tournesol.zip")

# generative_model = GenerativeModel.load("tests/generative_model/test_generative_model.json")
# s = generative_model()
# s.save("tests/pipeline/saved")

# s = State.load("tests/pipeline/saved")
pipeline= Sequential.load("tests/pipeline/test_pipeline.json")
states = [ State.load(f"tests/pipeline/saved/{seed}") for seed in range(5) ]

# for seed in range(5):
    # s = states[seed]
    
s = states[0]
# t = pipeline.aggregation.state2state_function(s)
# s = pipeline.aggregation.state2state_function(s, save_directory=f"tests/pipeline/saved/{seed}")
# s = pipeline.post_process.state2state_function(s, save_directory=f"tests/pipeline/saved/{seed}")


