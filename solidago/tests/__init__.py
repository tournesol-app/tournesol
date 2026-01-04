from solidago import *

import logging.config
logging.config.fileConfig("tests/info.conf")

source = "tests/experiments/engagement_bias.yaml"
experiment = Experiment.load(source, ignore_ongoing_run=True)

experiment()