from solidago.voting_rights import VotingRights
from solidago.scoring_model import ScoringModel
from solidago.privacy_settings import PrivacySettings
from solidago.judgments import DataFrameJudgments
from solidago.pipeline import Pipeline

import pandas as pd
import numpy as np

__all__ = ["users", "vouches", "entities", "privacy", "judgments"]


np.random.seed(0)

#######################################
##                                   ##
##   Basic Generation of Test Data   ##
##                                   ##
#######################################

n_tests = 5

users = [
    pd.DataFrame(columns=["is_pretrusted"]),
    pd.DataFrame(dict(is_pretrusted=[True, False, False, True, True])),
    pd.DataFrame(dict(
        is_pretrusted=[True, False, False, True, True]
    ), index=[0, 4, 2, 8, 6]),
    pd.DataFrame(dict(
        is_pretrusted=(np.arange(5) % 3 == 0),
        svd0=[1, 2, 5, 2, 1],
        svd1=[7, 2, 0, 1, 9]
    )),
    pd.DataFrame(dict(
        is_pretrusted=np.random.random(20) < 0.20,
        svd0=np.random.normal(0, 1, 20),
        svd1=np.random.normal(0, 1, 20),
        svd2=np.random.normal(0, 1, 20),
        svd3=np.random.normal(0, 1, 20),
        svd4=np.random.normal(0, 1, 20)
    ), index=2 * np.arange(20) + 3)
]
for u in users:
    u.index.name = "user_id"

vouches = [
    pd.DataFrame(columns=["voucher", "vouchee", "vouch"]),
    pd.DataFrame(dict(
        voucher=[0, 4, 1, 2],
        vouchee=[1, 1, 2, 3],
        vouch=[1, 1, 1, 1]
    )),
    pd.DataFrame(dict(
        voucher=[0, 4, 8, 2],
        vouchee=[4, 8, 4, 4],
        vouch=[1, 1, 1, 1]
    )),
    pd.DataFrame(dict(
        voucher=[0, 1, 2, 3],
        vouchee=[4, 4, 4, 4],
        vouch=[1, 1, 1, 1]
    )),
    pd.DataFrame(dict(
        voucher=2 * np.random.randint(0, 20, 80) + 3,
        vouchee=2 * np.random.randint(0, 20, 80) + 3,
        vouch=np.random.random(80)
    ))
]
vouches[4]["vouchee"] += 2 * (vouches[4]["vouchee"] == vouches[4]["voucher"])
vouches[4]["vouchee"] = ((vouches[4]["vouchee"] - 3) % 40) + 3

entities = [
    pd.DataFrame(),
    pd.DataFrame(index=[0, 1]),
    pd.DataFrame(index=[1, 6, 2]),
    pd.DataFrame(dict(
        svd0=[-1, 2, -1, 0, 0],
        svd1=[0, 0, 6, 4, 2]
    )),
    pd.DataFrame(dict(
        svd0=np.random.normal(0, 1, 50),
        svd1=np.random.normal(0, 1, 50),
        svd2=np.random.normal(0, 1, 50),
        svd3=np.random.normal(0, 1, 50),
        svd4=np.random.normal(0, 1, 50)
    ), index=3*np.arange(50) + 5)
]
for e in entities:
    e.index.name = "entity_id"

privacy = [
    PrivacySettings(),
    PrivacySettings({
        0: { 0: True,  1: True, 2: False, 3: True, 4: False },
        1: { 0: False, 1: True, 2: False, 3: True, 4: True }
    }),
    PrivacySettings({ 
        1: { 0: True,  4: True, 2: False, 8: True },
        6: { 0: False, 2: False, 8: True, 6: True },
        2: { 0: True, 4: True, 2: True, 6: True }
    }),
    PrivacySettings({
        0: { 0: True,  1: True, 2: False, 3: True, 4: False },
        1: { 1: True, 2: False, 3: True, 4: False },
        2: { 0: False,  1: True, 3: True, 4: False },
        3: { 0: True,  1: True, 3: True, 4: False },
        4: { 0: True,  1: True, 2: True, 3: True }
    }),
    PrivacySettings()
]
for _ in range(20 * 10):
    user = 2 * np.random.randint(20) + 3
    entity = 3 * np.random.randint(50) + 5
    privacy[4][user, entity] = (np.random.random() < 0.1)

judgments = [
    DataFrameJudgments(),
    DataFrameJudgments(pd.DataFrame(dict(
        user_id=[0, 1, 2, 3, 4],
        entity_a=[0, 0, 1, 0, 1],
        entity_b=[1, 1, 0, 1, 0],
        comparison=[-5, 3, -4, -8, -10],
        comparison_max=[10, 10, 10, 10, 10]
    ))),
    DataFrameJudgments(pd.DataFrame(dict(
        user_id=[0, 0, 0, 2, 2, 4, 6, 8],
        entity_a=[1, 2, 1, 2, 6, 1, 6, 1],
        entity_b=[6, 6, 2, 1, 1, 2, 2, 6],
        comparison=[-5, 3, -4, -8, -10, 2, 4, -4],
        comparison_max=[10, 10, 10, 10, 10, 10, 10, 10]
    ))),
    DataFrameJudgments(pd.DataFrame(dict(
        user_id= [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 3, 3, 3, 3, 3, 3, 4, 4, 4],
        entity_a=[0, 2, 4, 0, 1, 4, 3, 4, 0, 2, 1, 0, 4, 0, 0, 0, 0, 2, 4, 0, 1, 2],
        entity_b=[2, 3, 3, 2, 2, 3, 2, 1, 4, 3, 0, 4, 1, 1, 2, 3, 4, 3, 3, 1, 2, 3],
        comparison=    [-5,3,-4,-3,-3, 2, 4,-4, 3, 2, 1, 3, 4, 1, 2, 1, 2, 0,-1, 2,-1,-2],
        comparison_max=[5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5]
    ))),
    DataFrameJudgments(),
]
for entity in privacy[4].entities():
    for user in privacy[4].users(entity):
        for entity_bis in privacy[4].entities():
            if np.random.random() <= 0.8:
                continue
            comparison_max = np.random.random() * 10
            comparison = (2 * np.random.random() - 1) * comparison_max
            judgments[4].comparisons.loc[len(judgments[4].comparisons)] = [
                user, entity, entity_bis,
                comparison, comparison_max
            ]


#######################################
##                                   ##
##      Learning Pipeline Data       ##
##                                   ##
#######################################

pipeline = Pipeline()
trusts = [
    pipeline.trust_propagation(users[test], vouches[test])
    for test in range(n_tests)
]

#voting_rights = [
#   pipeline.voting_rights(trusts[test], vouches[test], privacy[test])
#   for test in range(n_tests)
#]

