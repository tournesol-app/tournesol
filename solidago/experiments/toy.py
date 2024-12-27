import sys
import json
import os
import logging
import numpy as np
import pandas as pd

from solidago import *


print("Loading tiny tournesol")
t = TournesolExport("experiments/tiny_tournesol.zip")

assert "biscuissec" in t.users, t.users
assert t.users.loc["le_science4all", "trust_score"] == 1
assert "NatNgs" in t.vouches["aidjango"]
assert t.vouches["aidjango", "biscuissec", "ProofOfPersonhood"] == (1, 0)
assert "KMuBHtR8zUk" in t.entities
assert "reliability" in t.criteria
assert t.criteria.get("engaging")["description"] == 'Engaging and thought-provoking'
assert isinstance(t.made_public, AllPublic)
assert len(t.assessments) == 0
assert len(t.comparisons) == 10295
assert len(t.comparisons["amatissart", "largely_recommended"]) == 11
assert t.voting_rights["Tit0uan", "SlQMxMr6t2w", "largely_recommended"] == 1
assert len(t.voting_rights["Tit0uan"]) == 39
assert "lpfaucon" in t.user_models
assert len(t.user_models["Zerathyon"].to_df()) == 2
assert len(t.voting_rights["lpfaucon"]) == len(t.user_models["lpfaucon"].to_df())
assert t.user_models["lpfaucon"]("ZMQbHMgK2rw", "largely_recommended").value == 81.02
assert t.global_model("009AGoQfVxA", "largely_recommended").to_triplet() == (4.37, 130.51, 130.51)

print("Saving tiny tournesol")
t.save("experiments/save_tiny_tournesol")

print("Reloading saved tiny tournesol")
t2 = State.load("experiments/save_tiny_tournesol")

assert "biscuissec" in t2.users, t2.users
assert t2.users.loc["le_science4all", "trust_score"] == 1
assert "NatNgs" in t2.vouches["aidjango"]
assert t2.vouches["aidjango", "biscuissec", "ProofOfPersonhood"] == (1, 0)
assert "KMuBHtR8zUk" in t2.entities
assert "reliability" in t2.criteria
assert t2.criteria.get("engaging")["description"] == 'Engaging and thought-provoking'
assert isinstance(t2.made_public, AllPublic)
assert len(t2.assessments) == 0
assert len(t2.comparisons) == 10295
assert len(t2.comparisons["amatissart", "largely_recommended"]) == 11
assert t.comparisons["amatissart", "largely_recommended"].get("Ud2rUxmrhYI")["as_left"]["vqDbMEdLiCs"]["comparison"] == -3
assert t2.voting_rights["Tit0uan", "SlQMxMr6t2w", "largely_recommended"] == 1
assert len(t2.voting_rights["Tit0uan"]) == 39
assert "lpfaucon" in t2.user_models
assert len(t2.user_models["Zerathyon"].to_df()) == 2
assert len(t2.voting_rights["lpfaucon"]) == len(t2.user_models["lpfaucon"].to_df())
assert t2.user_models["lpfaucon"]("ZMQbHMgK2rw", "largely_recommended").value == 81.02
assert t2.global_model("009AGoQfVxA", "largely_recommended").to_triplet() == (4.37, 130.51, 130.51)

with open("experiments/toy.json") as f: hps = json.load(f)

print("Loading toy generative model")
generative_model = GenerativeModel.load(hps["generative_model"])

users = generative_model.user_gen(30)
vouches = generative_model.vouch_gen(users)
entities = generative_model.entity_gen(100)
criteria = generative_model.criterion_gen(2)
made_public, assessments, comparisons = generative_model.engagement_gen(users, entities, criteria)

print("Generating data")
s = generative_model(30, 100, 2, 0)

print("Saving data")
s.save("experiments/generated_model")

print("Reloading saved data")
s2 = State.load("experiments/generated_model")

assert "17" in s2.users
assert s.users.get("10")["n_comparisons"] == s2.users.get("10")["n_comparisons"]
assert s.vouches["24", "11", "ProofOfPersonhood"] == s2.vouches["24", "11", "ProofOfPersonhood"]
assert "73" in s2.entities
assert len(s2.entities) == 100
assert "1" in s2.criteria
assert len(s2.criteria) == 2
assert s.made_public["21"] == s2.made_public["21"]
assert set(s.assessments["12", "0"]["entity_id"]) == set(s2.assessments["12", "0"]["entity_id"])
assert set(s.comparisons["0", "0", "57"]["as_left"].keys()) == set(s2.comparisons["0", "0", "57"]["as_left"].keys())

# pipeline = Pipeline.from_json(hps["pipeline"])

# users, vouches, entities, privacy, judgments = synthetic_data
# users, voting_rights, user_models, global_model = pipeline(users_in, vouches, entities, privacy, judgments)

# t = tournesol_data.get_pipeline_kwargs(criterion="reliability")


