import sys
import json
import os
import logging
import numpy as np
import pandas as pd

from solidago import *


print("Loading tiny tournesol")
t = TournesolExport("experiments/tiny_tournesol.zip")

print("Saving tiny tournesol")
t.save("experiments/save_tiny_tournesol")

print("Reloading saved tiny tournesol")
t2 = State.load("experiments/save_tiny_tournesol")

assert "biscuissec" in t2.users
assert t2.users.loc["le_science4all", "trust_score"] == 1
assert "NatNgs" in t2.vouches["aidjango"]["ProofOfPersonhood"]
assert t2.vouches["aidjango", "biscuissec", "ProofOfPersonhood"] == (1, 0)
assert "KMuBHtR8zUk" in t2.entities
assert "reliability" in t2.criteria
assert t2.criteria.get("engaging")["description"] == 'Engaging and thought-provoking'
assert isinstance(t2.made_public, AllPublic)
assert "lpfaucon" in t2.user_models
assert len(t2.judgments.assessments) == 0
assert len(t2.judgments.comparisons) == 10295
# assert len(t2.judgments.comparisons["amatissart", "largely_recommended"]) == 1
assert len(t2.user_models["Zerathyon"].to_df()) == 2

with open("experiments/toy.json") as f: hps = json.load(f)

print("Loading toy generative model")
generative_model = GenerativeModel.load(hps["generative_model"])

print("Generating data")
s = generative_model(30, 100, 0)

print("Saving data")
s.save("experiments/generated_model")

print("Reloading saved data")
s2 = State.load("experiments/generated_model")

# pipeline = Pipeline.from_json(hps["pipeline"])

# users, vouches, entities, privacy, judgments = synthetic_data
# users, voting_rights, user_models, global_model = pipeline(users_in, vouches, entities, privacy, judgments)

# t = tournesol_data.get_pipeline_kwargs(criterion="reliability")


