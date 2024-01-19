from solidago.voting_rights import VotingRights
from solidago.scoring_model import ScoringModel
from solidago.privacy_settings import PrivacySettings
from solidago.judgments import DataFrameJudgments

import pandas as pd
import numpy as np


np.random.seed(0)

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
        is_pretrusted=np.random.random(100) < 0.20,
        svd0=np.random.normal(0, 1, 100),
        svd1=np.random.normal(0, 1, 100),
        svd2=np.random.normal(0, 1, 100),
        svd3=np.random.normal(0, 1, 100),
        svd4=np.random.normal(0, 1, 100)
    ), index=2 * np.arange(100) + 3)
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
        voucher=np.random.randint(0, 100, 200),
        vouchee=np.random.randint(0, 100, 200),
        vouch=np.random.random(200)
    ))
]
vouches[4]["vouchee"] = vouches[4]["vouchee"] + (vouches[4]["vouchee"] == vouches[4]["voucher"])

entities = [
    pd.DataFrame(),
    pd.DataFrame(index=[0, 1]),
    pd.DataFrame(index=[1, 6, 2]),
    pd.DataFrame(dict(
        svd0=[-1, 2, -1, 0, 0],
        svd1=[0, 0, 6, 4, 2]
    )),
    pd.DataFrame(dict(
        svd0=np.random.normal(0, 1, 300),
        svd1=np.random.normal(0, 1, 300),
        svd2=np.random.normal(0, 1, 300),
        svd3=np.random.normal(0, 1, 300),
        svd4=np.random.normal(0, 1, 300)
    ), index=3*np.arange(300) + 5)
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
for _ in range(100 * 50):
    user = 2 * np.random.randint(100) + 3
    entity = 3 * np.random.randint(300) + 5
    privacy[4][user, entity] = (np.random.random() < 0.1)

judgments = [
    DataFrameJudgments(),
    DataFrameJudgments(pd.DataFrame(dict(
        user_id=[0, 1, 2, 3, 4],
        entity_a=[0, 0, 1, 0, 1],
        entity_b=[1, 1, 0, 1, 0],
        score=[-5, 3, -4, -8, -10],
        comparison_max=[10, 10, 10, 10, 10]
    ))),
    DataFrameJudgments(),
    DataFrameJudgments(),
    DataFrameJudgments(),
]

def test_privacy():
    assert privacy[2][0, 1]
