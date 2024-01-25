from solidago import PrivacySettings

from solidago.voting_rights import VotingRights
from solidago.scoring_model import DirectScoringModel
from solidago.judgments import DataFrameJudgments
from solidago.pipeline import Pipeline

import pandas as pd
import numpy as np


np.random.seed(0)

def print_user_models(models):
    print "{\n    " + ",\n    ".join([
        f"{user}: DirectScoringModel(" + "{\n        " + ",\n        ".join([
            f"{entity}: {str(models[user](entity, entities.loc[entity]))}"
            for entity in models[user].scored_entities(entities)
        ]) + "\n    })"
        for user in models
    ) + "\n}"

def print_global_model(model):
    print "DirectScoringModel({\n    " + "\n    ".join([
            f"{entity}: {str(models[user](entity, entities.loc[entity]))}"
            for entity in models[user].scored_entities(entities)
        ]) + "\n})"

pipeline = Pipeline()

