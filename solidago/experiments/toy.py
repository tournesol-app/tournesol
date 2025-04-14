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
    # s = TournesolExport("experiments/tournesol_dataset.zip")
    # s.save("experiments/tournesol_processed")
    s = State.load("experiments/tournesol_processed")
    
    # users, entities, vouches, made_public = s.users, s.entities, s.vouches, s.made_public
    # assessments, comparisons, voting_rights = s.assessments, s.comparisons, s.voting_rights
    # user_models, global_model = s.user_models, s.global_model

with time(logger, "Running the pipeline"):
    # s.user_models = UserModels() # Does not use current scores as init
    # t = pipeline(s, "experiments/tiny_tournesol_processed")
    t = pipeline(s, "experiments/tournesol_processed", skip_steps={0,1,2,3})
    
    # s1 = pipeline.trust_propagation.state2state_function(s)
    # s2 = pipeline.preference_learning.state2state_function(s1)
    # s3 = pipeline.voting_rights.state2state_function(s2)
    # s4 = pipeline.scaling.state2state_function(s3)
    # s5 = pipeline.aggregation.state2state_function(s4)
    # s6 = pipeline.post_process.state2state_function(s5)

import numpy as np
from solidago import *
from solidago.modules.scaling import Mehestan, LipschitzStandardize, LipschitzQuantileShift

states = [ State.load(f"tests/saved/{seed}") for seed in range(5) ]
seed = 0
self = Mehestan(
    lipschitz=1., 
    min_scaler_activity=1.,
    n_scalers_max=5, 
    privacy_penalty=0.5,
    user_comparison_lipschitz=10.,
    p_norm_for_multiplicative_resilience=4.0,
    n_entity_to_fully_compare_max=100,
    error=1e-5,
    max_workers=1
)
s = states[seed]
users, entities, made_public = s.users, s.entities, s.made_public
user_models = UserModels(s.user_models.user_directs)
scores = user_models(entities)
fixed_args = users, entities, made_public
args_list = [(c, scores.get(criterion=c)) for c in user_models.criteria()]
criterion, scores = next(iter(args_list))
activities, is_scaler = self.compute_activities_and_scalers(users, made_public, scores)
scalers, nonscalers = set(), set()
for index, user in enumerate(users):
    (scalers if is_scaler[index] else nonscalers).add(user.name)
scaler_scores, nonscaler_scores = scores[scalers], scores[nonscalers]
scale_scalers_to_scalers_args = (users, made_public, scaler_scores, scaler_scores, True)
scalee_scores = scaler_scores
username = next(iter(scores.keys("username")))
made_public = made_public[username]
scores = scores[username]

scalee_model_norms = self.compute_model_norms(made_public, scalee_scores)

scaler_scales, scaler_scores = self.scale_to_scalers(*scale_scalers_to_scalers_args)
scale_nonscalers_to_scalers_args = (users, made_public, scaler_scores, nonscaler_scores)
nonscaler_scales, _ = self.scale_to_scalers(*scale_nonscalers_to_scalers_args)

self.scale_criterion(*fixed_args, s)
self.results2output(users, user_models, results)
users, scaled_models = self(users, entities, made_public, user_models)