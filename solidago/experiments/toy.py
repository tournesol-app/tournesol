import sys
import json
import os
import logging
import numpy as np
import pandas as pd

from solidago import *


t = TournesolExport("tests/tiny_tournesol.zip")

with open("experiments/toy.json") as f: hps = json.load(f)
gen = GenerativeModel.load(hps["generative_model"])
    
users = gen.user_gen(30)
vouches = gen.vouch_gen(users)
entities = gen.entity_gen(100)
criteria = gen.criterion_gen(2)
made_public, assessments, comparisons = gen.engagement_gen(users, entities, criteria)
assessments = gen.assessment_gen(users, entities, criteria, made_public, assessments)
comparisons = gen.comparison_gen(users, entities, criteria, made_public, comparisons)

s = generative_model(30, 100, 2, 0)

# pipeline = Pipeline.from_json(hps["pipeline"])

# users, vouches, entities, privacy, judgments = synthetic_data
# users, voting_rights, user_models, global_model = pipeline(users_in, vouches, entities, privacy, judgments)

# t = tournesol_data.get_pipeline_kwargs(criterion="reliability")


