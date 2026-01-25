from solidago import *
from solidago.primitives.timer import time
from solidago.functions.parallelized import ParallelizedPollFunction

import logging.config

logging.config.fileConfig("tests/info.conf")

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
    if n <= 1:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

def primes(base_value: int, n_values: int):
    numbers = range(base_value, base_value + 2 * n_values, 2)
    for max_workers in (1, 2, 6, 15):
        with time(logging, f"Prime listing with max_workers={max_workers}"):
            results = ParallelizedPollFunction.threading(max_workers, is_prime, list(numbers))
            primes = [n for n, prime in zip(numbers, results) if prime]
            print(f"Found {len(primes)} primes")

class PrimeFunction(ParallelizedPollFunction):
    def __init__(self, base_value: int, n_values: int, max_workers = None):
        super().__init__(max_workers)
        self.base_value = base_value
        self.n_values = n_values

    def _variables(self) -> list:
        return range(self.base_value, self.base_value + 2 * self.n_values, 2)
    
    def _args(self, variable: int, nonargs) -> list:
        return [variable]
    
    def thread_function(self, variable) -> bool:
        if variable <= 1:
            return False
        for i in range(2, int(variable ** 0.5) + 1):
            if variable % i == 0:
                return False
        return True
    
    def _process_results(self, variables: list, nonargs_list: list, results: list, args_lists: list) -> Poll:
        primes = [n for n, prime in zip(variables, results) if prime]
        print(f"Found {len(primes)} primes")

def primes2(base_value: int, n_values: int):
    for max_workers in (1, 2, 6, 15):
        with time(logging, f"Prime listing with max_workers={max_workers}"):
            PrimeFunction(base_value, n_values, max_workers)()

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
        with time(logging, f"Preference learning with max_workers={max_workers}"):
            preference_learning = functions.NumbaUniformGBT(max_workers=max_workers)
            preference_learning.poll2objects_function(poll)

def scoring():
    # poll = TournesolExport("tests/tournesol_dataset.zip")
    # poll = TournesolExport("tests/tiny_tournesol.zip")
    poll = Poll.load("experiments/tournesol_processed")
    # poll.comparisons = poll.comparisons.get(criterion={"largely_recommended"}).reorder("username")
    for max_workers in (1, 2, 6, 15):
        with time(logging, f"User model scores with max_workers={max_workers}"):
            _ = poll.user_models(max_workers=max_workers)

def pipeline(step = None, tiny = True):
    for max_workers in (1,):
        with time(logging, f"Pipeline with n_workers={max_workers}"):
            poll = TournesolExport(f"tests/{'tiny_tournesol' if tiny else 'tournesol_dataset'}.zip")
            with time(logging, "Filtering"):
                pass
#                poll = functions.Filtering(criteria={"largely_recommended"})(poll)
            pipeline = load("src/solidago/functions/tournesol_full.yaml", max_workers=max_workers)
            assert isinstance(pipeline, Sequential)
            if isinstance(step, int):
                pipeline.modules[step].poll2poll_function(poll)
            elif isinstance(step, list):
                skip_steps = [i for i in range(len(pipeline.modules)) if i not in step]
                pipeline(poll, skip_steps=skip_steps)
            else:
                pipeline(poll, "tests/tournesol_processed")


if __name__ == "__main__":
    from datetime import datetime
    print(f"{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} Running tests")
    # results = basic_multithread(2)
    # prime_threading()
    # gbt()
    # pipeline(step=[0, 1, 4, 5, 6, 7], tiny=False)
    # primes2(835, 10000)
    # primes2(51305235249835, 10000)
    