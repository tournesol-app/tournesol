import json
import logging
import numpy as np

from solidago import *
from solidago.primitives.timer import time

logger = logging.getLogger(__name__)

with open("experiments/engagement_bias.json") as json_file:
    hps = json.load(json_file)

generator = Generator.load(hps["generative_model"])
pipeline = Sequential.load(hps["pipeline"])

with time("Generating data", logger):
    poll = generator()

with time("Running pipeline", logger):
    poll = pipeline(poll)

truth = poll.entities.get_column("v0")
estimate = poll.global_model(poll.entities).value
correlation = np.corrcoef(truth, estimate)[0, 1]
logger.info(f"Successful run")

