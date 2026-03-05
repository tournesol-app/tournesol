from pathlib import Path

import logging.config
logging.config.fileConfig('experiments/info.conf')

import solidago as sdg
N_SEEDS = 3

generator = sdg.load("tests/generators/test_generator.yaml")
assert isinstance(generator, sdg.Generator)

pipeline = sdg.load("tests/save_load/pipeline.yaml", max_workers=1)
assert isinstance(pipeline, sdg.Sequential)


def save_generated_data(seed: int):
    assert isinstance(generator, sdg.Generator)
    generator.seed = seed
    generator.fn().save(f"tests/save_load/saved/{seed}")

def save_all_generated_data():
    for seed in range(N_SEEDS):
        save_generated_data(seed)

def save_pipeline_results(seed: int, skip_steps={}):
    assert isinstance(pipeline, sdg.Sequential)
    pipeline.seed = seed
    directory = f"tests/save_load/saved/{seed}"
    poll = sdg.Poll.load(directory)
    pipeline.fn(poll, directory, skip_steps)

def save_all_pipeline_results(skip_steps={}):
    for seed in range(N_SEEDS):
        save_pipeline_results(seed, skip_steps)

def step_by_step(sequential: sdg.Sequential, poll: sdg.Poll | None, seed: int = 0) -> list[sdg.Poll]:
    sequential.seed = seed
    assert isinstance(sequential, sdg.Sequential)
    polls = [sdg.Poll() if poll is None else poll]
    polls.append(sequential[0](polls[-1]))
    polls.append(sequential[1](polls[-1]))
    polls.append(sequential[2](polls[-1]))
    polls.append(sequential[3](polls[-1]))
    polls.append(sequential[4](polls[-1]))
    return polls

def step_by_step_generator() -> list[sdg.Poll]:
    generator.seed = 0
    polls = [sdg.Poll()]
    for f in generator:
        polls.append(f(polls[-1]))
    return polls

if __name__ == "__main__":
    for seed in range(N_SEEDS):
        path = Path(f"tests/save_load/saved/{seed}")
        if path.is_dir():
            for f in path.iterdir():
                if f.is_file():
                    f.unlink()
    save_all_generated_data()
    save_all_pipeline_results()

