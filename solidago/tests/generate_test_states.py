from solidago import *

generator = Generator.load("tests/generators/test_generator.json")
pipeline = Sequential.load("tests/modules/test_pipeline.json")

def save_generated_data(seed=None):
    if seed is None:
        seed = range(5)
    if isinstance(seed, int):
        generator(seed=seed).save(f"tests/modules/saved/{seed}")
    else:
        for s in seed:
            save_generated_data(s)
        
def save_pipeline_results(seed=None):
    if seed is None:
        seed = range(5)
    if isinstance(seed, int):
        directory = f"tests/modules/saved/{seed}"
        pipeline(State.load(directory), directory)
    else:
        for s in seed:
            save_generated_data(s)
        
save_generated_data()
save_pipeline_results()

