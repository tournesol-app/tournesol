import sys
import json
import os
import logging
import numpy as np
import pandas as pd

import solidago


print("Loading tiny tournesol")
t = solidago.state.TournesolExport("experiments/tiny_tournesol.zip")

with open("experiments/toy.json") as f: hps = json.load(f)

print("Loading toy generative model")
generative_model = solidago.generative_model.GenerativeModel.load(hps["generative_model"])

print("Generating data")
s = generative_model(30, 100, 0)

print("Saving data")
s.save("experiments/generated_model")

print("Reloading saved data")
s2 = solidago.state.State.load("experiments/generated_model")

# pipeline = Pipeline.from_json(hps["pipeline"])

# users, vouches, entities, privacy, judgments = synthetic_data
# users, voting_rights, user_models, global_model = pipeline(users_in, vouches, entities, privacy, judgments)

# t = tournesol_data.get_pipeline_kwargs(criterion="reliability")


