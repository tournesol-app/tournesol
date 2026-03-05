from typing import Callable
from solidago import *
from solidago.primitives.timer import time
from solidago.poll_functions.parallelized import ParallelizedPollFunction
from solidago.poll_functions.preference_learning import FlexibleGeneralizedBradleyTerry
from solidago.poll_functions.preference_learning.gbt.root_law import *

import logging.config

logging.config.fileConfig("tests/info.conf")

def simple():
    source = "tests/experiments/simple.yaml"

    experiment = Experiment.load(source, ignore_ongoing_run=True, max_workers=15)
    poll, generator, poll_functions = experiment.extract_poll_generator_functions([0])
    poll = generator.fn(poll)

    with time("SimpleExperiment"):
        poll2 = poll_functions(poll)
    
    return source, experiment, poll, poll2, generator, poll_functions

def gbt_poll0():
    from solidago.poll_functions.preference_learning.numba_generalized_bradley_terry import NumbaUniformGBT
    poll = Poll.load(f"tests/saved/0")
    f = NumbaUniformGBT(
        prior_std=7.0, 
        uncertainty_nll_increase=1.0, 
        max_uncertainty=1e3, 
        max_workers=2
    )
    poll2 = f(poll)
    return poll, f, poll2

def f(score_diffs: NDArray) -> NDArray:
    score_diffs_abs = np.abs(score_diffs)
    with np.errstate(all='ignore'):
        return np.where(
            score_diffs_abs > 1e-1,
            np.where(
                score_diffs_abs < 20.0,
                np.log(np.sinh(score_diffs) / score_diffs),
                score_diffs_abs - np.log(2) - np.log(score_diffs_abs),
            ),
            score_diffs_abs ** 2 / 6 - score_diffs_abs ** 4 / 180,
        )


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
    # gbt = FlexibleGeneralizedBradleyTerry()
    print(f(np.array([1, 2, 5], dtype=np.float64)))