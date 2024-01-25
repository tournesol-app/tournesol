import logging
import numpy as np
import pandas as pd

from solidago.pipeline.inputs import TournesolInputFromPublicDataset
from solidago.judgments import DataFrameJudgments
from solidago.privacy_settings import PrivacySettings
from solidago.pipeline import Pipeline


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logger.addHandler(ch)

logger.info("Retrieve public dataset")
dataset = TournesolInputFromPublicDataset.download()

logger.info("Preprocessing data for the pipeline")
users = dataset.users
users = users.assign(is_pretrusted=(users["trust_score"] >= 0.8))
vouches = pd.DataFrame(columns=["voucher", "vouchee", "vouch"])
entities_indices = set(dataset.comparisons["entity_a"]) | set(dataset.comparisons["entity_b"])
entities = pd.DataFrame(index=list(entities_indices))
privacy = PrivacySettings()
for _, row in data.comparisons.iterrows():
    privacy[row["user_id"], row["entity_a"]] = True
    privacy[row["user_id"], row["entity_b"]] = True
dataset.comparisons.rename(columns={"score": "comparison"}, inplace=True)
dataset.comparisons = dataset.comparisons.assign(comparison_max=[10] * len(dataset.comparisons))

criteria = set(data.comparisons["criteria"])
for criterion in criteria:
    logger.info(f"Running the pipeline for criterion `{criterion}`")
    comparisons = dataset.comparisons[dataset.comparisons["criteria"] == criterion]
    judgments = DataFrameJudgments(comparisons=dataset.comparisons)
    output = Pipeline()(users, vouches, entities, privacy, judgments)
    users, voting_rights, user_models, global_model = output
logger.info(f"Successful pipeline run.")
