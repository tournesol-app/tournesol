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


generative_model = GenerativeModel.load("tests/generative_model/test_generative_model.json")
states = [ State.load(f"tests/modules/saved/{seed}") for seed in range(5) ]
tiny = TournesolExport("tests/tiny_tournesol.zip")

# t = TournesolExport("experiments/tournesol.zip")
# t = State.load("experiments/saved_tournesol")
# pipeline = solidago.Sequential.load("tests/pipeline/test_pipeline.json")

# r = pipeline(t)

