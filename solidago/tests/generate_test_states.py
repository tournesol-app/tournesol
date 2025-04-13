from pathlib import Path

import logging.config
logging.config.fileConfig('experiments/info.conf')

from solidago import *

generator = Generator.load("tests/generators/test_generator.json")
pipeline = Sequential.load("tests/modules/test_pipeline.json")

def save_generated_data(seed=None):
    if seed is None:
        seed = range(5)
    if isinstance(seed, int):
        generator(seed=seed).save(f"tests/saved/{seed}")
    else:
        for s in seed:
            save_generated_data(s)
        
def save_pipeline_results(seed=None, skip_steps={}):
    if seed is None:
        seed = range(5)
    if isinstance(seed, int):
        directory = f"tests/saved/{seed}"
        pipeline(State.load(directory), directory, skip_steps)
    else:
        for s in seed:
            save_pipeline_results(s, skip_steps)

if __name__ == "__main__":
    for seed in range(5):
        path = Path(f"tests/saved/{seed}")
        if path.is_dir():
            for f in path.iterdir():
                if f.is_file():
                    f.unlink()
    save_generated_data()
    save_pipeline_results(skip_steps={0, 1, 2, 3, 4, 5})

