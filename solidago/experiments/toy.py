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
from solidago.primitives.optimize import *


t = TournesolExport("tests/tiny_tournesol.zip")
generative_model = GenerativeModel.load("tests/generative_model/test_generative_model.json")
pipeline= Sequential.load("tests/pipeline/test_pipeline.json")
s = [ State.load(f"tests/pipeline/saved/{seed}") for seed in range(5) ]

u = pipeline(t)
