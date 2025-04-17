import logging.config
logging.config.fileConfig('experiments/info.conf')
from solidago.primitives.timer import time

logger = logging.getLogger(__name__)

with time(logger, "Loading packages and modules"):
    import sys, json, os, timeit
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    from pandas import DataFrame, Series
    
    import solidago
    from solidago import *
    from solidago.primitives.datastructure import *
    from solidago.primitives.lipschitz import *
    from solidago.primitives.optimize import *
    
    # generator = Generator.load("tests/generators/test_generator.json")
    # pipeline = Sequential.load("tests/modules/test_pipeline.json", max_workers=os.cpu_count() - 1)
    pipeline = Sequential.load("src/solidago/modules/tournesol_full.json", max_workers=os.cpu_count() - 1)
    # pipeline = Sequential.load("src/solidago/modules/tournesol_full.json", max_workers=1)

with time(logger, "Loading input states"):
    # states = [ State.load(f"tests/saved/{seed}") for seed in range(5) ]
    # processed_states = [ pipeline(states[seed], f"tests/saved/{seed}") for seed in range(5) ]
    # s = State.load("tests/saved/0")
    # s = generator(seed=0)
    
    # s = TournesolExport("tests/tiny_tournesol.zip")
    # s.save("experiments/tiny_tournesol_processed")
    # s = State.load("experiments/tiny_tournesol_processed")
    
    # dfs = TournesolExport.load_dfs("experiments/tournesol_dataset.zip")
    s = TournesolExport("experiments/tournesol_dataset.zip")
    s.save("experiments/tournesol_processed")
    # s = State.load("experiments/tournesol_processed")
    
    # users, entities, vouches, made_public = s.users, s.entities, s.vouches, s.made_public
    # assessments, comparisons, voting_rights = s.assessments, s.comparisons, s.voting_rights
    # user_models, global_model = s.user_models, s.global_model

with time(logger, "Running the pipeline"):
    s.user_models = UserModels() # Does not use current scores as init
    
    # t = pipeline(s, "experiments/tiny_tournesol_processed")
    t = pipeline(s, "experiments/tournesol_processed")

    # s1 = pipeline.trust_propagation.state2state_function(s)
    # s2 = pipeline.preference_learning.state2state_function(s1)
    # s3 = pipeline.voting_rights.state2state_function(s2)
    # s4 = pipeline.scaling.state2state_function(s3)
    # s5 = pipeline.aggregation.state2state_function(s4)
    # s6 = pipeline.post_process.state2state_function(s5)