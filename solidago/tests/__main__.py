from solidago import *
from solidago.primitives.timer import time
from solidago.functions.parallelized import ParallelizedPollFunction
from solidago.functions.preference_learning import FlexibleGeneralizedBradleyTerry
from solidago.functions.preference_learning.gbt.root_law import *

import logging.config

logging.config.fileConfig("tests/info.conf")

def simple():
    source = "tests/experiments/simple.yaml"

    experiment = Experiment.load(source, ignore_ongoing_run=True, max_workers=15)
    poll, generator, poll_functions = experiment.extract_poll_generator_functions([0])
    poll = generator(poll)

    with time(logging, "SimpleExperiment"):
        poll2 = poll_functions(poll)
    
    return source, experiment, poll, poll2, generator, poll_functions

def gbt_poll0():
    poll = Poll.load(f"tests/saved/0")
    f = functions.preference_learning.NumbaUniformGBT(
        prior_std=7.0, 
        uncertainty_nll_increase=1.0, 
        max_uncertainty=1e3, 
        max_workers=2
    )
    poll2 = f(poll)
    return poll, f, poll2


if __name__ == "__main__":
    from datetime import datetime
    print(f"{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} Running tests")
    # source, experiment, poll, poll2, generator, poll_functions = simple()
    # poll, f, poll2 = gbt_poll()
    # results = basic_multithread(2)
    # prime_threading()
    # gbt()
    # pipeline(step=[0, 1, 4, 5, 6, 7], tiny=False)
    # primes2(835, 10000)
    # primes2(51305235249835, 10000)
    gbt = FlexibleGeneralizedBradleyTerry()