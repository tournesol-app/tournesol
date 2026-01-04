from pathlib import Path

import logging.config
logging.config.fileConfig('experiments/info.conf')

from solidago import *
N_SEEDS = 3

generator = load("tests/generators/test_generator.yaml")
assert isinstance(generator, Generator)

pipeline = load("tests/modules/test_pipeline.yaml")
assert isinstance(pipeline, Sequential)


def save_generated_data(seed: int):
    generator.seed = seed
    generator().save(f"tests/saved/{seed}")

def save_all_generated_data():
    for seed in range(N_SEEDS):
        save_generated_data(seed)

def save_pipeline_results(seed: int, skip_steps={}):
    directory = f"tests/saved/{seed}"
    poll = Poll.load(directory)
    pipeline(poll, directory, skip_steps)

def save_all_pipeline_results(skip_steps={}):
    for seed in range(N_SEEDS):
        save_pipeline_results(seed, skip_steps)

if __name__ == "__main__":
    for seed in range(N_SEEDS):
        path = Path(f"tests/saved/{seed}")
        if path.is_dir():
            for f in path.iterdir():
                if f.is_file():
                    f.unlink()
    save_all_generated_data()
    save_all_pipeline_results()

