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
inputs = TournesolInputFromPublicDataset.download()

logger.info("Preprocessing data for the pipeline")
users, vouches, entities, privacy = inputs.get_pipeline_objects()

criteria = set(data.comparisons["criteria"])
for criterion in criteria:
    logger.info(f"Running the pipeline for criterion `{criterion}`")
    judgments = Judgments.from_tournesol(inputs, criterion)
    output = Pipeline()(users, vouches, entities, privacy, judgments)
    users, voting_rights, user_models, global_model = output
logger.info(f"Successful pipeline run.")
