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
assert t2.voting_rights["Tit0uan", "SlQMxMr6t2w", "largely_recommended"] == 1
assert len(t2.voting_rights["Tit0uan"]) == 39
assert "lpfaucon" in t2.user_models
assert len(t2.judgments.assessments) == 0
assert len(t2.judgments.comparisons) == 10295
assert len(t2.judgments.comparisons["amatissart", "largely_recommended"]) == 11
assert len(t2.user_models["Zerathyon"].to_df()) == 2
assert len(t2.voting_rights["lpfaucon"]) == len(t2.user_models["lpfaucon"].to_df())
assert t2.user_models["lpfaucon"]("ZMQbHMgK2rw", "largely_recommended").value == 81.02
assert t2.global_model("009AGoQfVxA", "largely_recommended").to_triplet() == (4.37, 130.51, 130.51)

with open("experiments/toy.json") as f: hps = json.load(f)

print("Loading toy generative model")
generative_model = GenerativeModel.load(hps["generative_model"])

# users = generative_model.user_gen(30)
# vouches = generative_model.vouch_gen(users)
# entities = generative_model.entity_gen(100)
# criteria = generative_model.criterion_gen(2)
# made_public, judgments = generative_model.engagement_gen(users, entities, criteria)

print("Generating data")
s = generative_model(30, 100, 2, 0)

print("Saving data")
s.save("experiments/generated_model")

print("Reloading saved data")
s2 = State.load("experiments/generated_model")

# pipeline = Pipeline.from_json(hps["pipeline"])

# users, vouches, entities, privacy, judgments = synthetic_data
# users, voting_rights, user_models, global_model = pipeline(users_in, vouches, entities, privacy, judgments)

# t = tournesol_data.get_pipeline_kwargs(criterion="reliability")


