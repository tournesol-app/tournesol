import sys
import json
import os
# import logging.config
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# logging.config.fileConfig('experiments/info.conf')

from pandas import DataFrame, Series
from pathlib import Path
from numba import njit

from solidago import *
from solidago.primitives.datastructure import *
from solidago.primitives.lipschitz import *
from solidago.primitives.optimize import *


generator = Generator.load("tests/generators/test_generator.json")
pipeline = Sequential.load("tests/modules/test_pipeline.json")

# from tests.generate_test_states import *
# save_generated_data()

# states = [ State.load(f"tests/modules/saved/{seed}") for seed in range(5) ]
# out = [ pipeline(s, skip_steps={3, 4, 5}) for s in states ]

s = State.load("tests/modules/saved/0")

# for seed in range(5):
    # directory = f"tests/modules/saved/{seed}"
    # pipeline(State.load(directory), directory, skip_steps={3, 4, 5})

# tiny = TournesolExport("tests/tiny_tournesol.zip")

# t = TournesolExport("experiments/tournesol.zip")
# t = State.load("experiments/saved_tournesol")
# pipeline = solidago.Sequential.load("tests/pipeline/test_pipeline.json")

# r = pipeline(t)

