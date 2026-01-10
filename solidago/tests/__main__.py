from functools import reduce
from solidago import *
from solidago.primitives.timer import time
from solidago.primitives.threading import threading

import logging.config
import math

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

def basic_multithread(max_workers):
    from concurrent.futures import ProcessPoolExecutor
    def thread(i, j):
        for iter in range(int(1e8)):
            if iter % int(1e7) == 0:
                print(f"{i}, {j}: {iter}")
        return i + j
    
    with time(logging, f"ProcessPool with max_workers={max_workers}"):
        with ProcessPoolExecutor(max_workers) as executor:
            results = executor.map(thread, range(10), [200] * 10)
    
    return results
    
def is_prime(n):
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False

    sqrt_n = int(math.floor(math.sqrt(n)))
    for i in range(3, sqrt_n + 1, 2):
        if n % i == 0:
            return (n, False)
    return (n, True)

def prime_threading():
    numbers = list(range(124315111353113, 124315111353113 + 10000, 2))
    for max_workers in (1, 2, 4, 8, 15):
        with time(logging, f"Primality test with n_workers={max_workers}"):
            result = threading(max_workers, is_prime, numbers)
        primes = [p for p, prime in result if prime]
        print(f"Found {len(primes)} primes")

def gbt():
    # poll = TournesolExport("tests/tournesol_dataset.zip")
    # poll = TournesolExport("tests/tiny_tournesol.zip")
    # poll.comparisons = poll.comparisons.get(criterion={"largely_recommended"}).reorder("username")
    generator = Generator([
        generators.users.Users(100, primitives.random.Normal(mean=[3.0, 0.0, 0.0])),
        generators.entities.Entities(100000, primitives.random.Normal(3)),
        generators.users.AddColumn("n_evaluated_entities", primitives.random.Poisson(10)),
        generators.users.AddColumn("n_comparisons_per_entity", primitives.random.Uniform(2.0, 10.0)),
        generators.engagements.Independent(generators.engagements.Uniform()),
        generators.comparisons.Independent(generators.comparisons.KnaryGBT(21, 10))
    ], seed=0)
    poll = generator()
    for max_workers in (1, 2, 6, 15):
        with time(logging, f"Preference learning with n_workers={max_workers}"):
            preference_learning = functions.NumbaUniformGBT(max_workers=max_workers)
            preference_learning.poll2objects_function(poll)

def scoring():
    # poll = TournesolExport("tests/tournesol_dataset.zip")
    # poll = TournesolExport("tests/tiny_tournesol.zip")
    poll = Poll.load("experiments/tournesol_processed")
    # poll.comparisons = poll.comparisons.get(criterion={"largely_recommended"}).reorder("username")
    for max_workers in (1, 2, 6, 15):
        with time(logging, f"User model scores with n_workers={max_workers}"):
            _ = poll.user_models(max_workers=max_workers)

def pipeline(tiny = True):
    poll = TournesolExport(f"tests/{'tiny_tournesol' if tiny else 'tournesol_dataset'}.zip")
    # poll = TournesolExport("tests/tiny_tournesol.zip")
    for max_workers in (1, 2, 4, 6, 15):
        with time(logging, f"Pipeline with n_workers={max_workers}"):
            pipeline = load("src/solidago/functions/tournesol_full.yaml", max_workers=max_workers)
            assert isinstance(pipeline, Sequential)
            # pipeline(poll, "tests/tournesol_processed")
            pipeline.modules[6].poll2poll_function(poll)

if __name__ == "__main__":
    # source, experiment, poll, poll2, generator, poll_functions = simple()
    # poll, f, poll2 = gbt_poll()
    # results = basic_multithread(2)
    # prime_threading()
    # gbt()
    pipeline(tiny=False)