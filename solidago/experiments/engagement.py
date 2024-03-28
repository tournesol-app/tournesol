import json
import logging
import numpy as np

from solidago.generative_model import GenerativeModel
from solidago.pipeline import Pipeline


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logger.addHandler(ch)

pipeline_logger = logging.getLogger("solidago.pipeline.pipeline")
pipeline_logger.setLevel(logging.INFO)
pipeline_ch = logging.StreamHandler()
pipeline_ch.setLevel(logging.INFO)
pipeline_logger.addHandler(pipeline_ch)


with open("experiments/engagement_bias.json") as json_file:
    hps = json.load(json_file)

generative_model = GenerativeModel.from_json(hps["generative_model"])
pipeline = Pipeline.from_json(hps["pipeline"])

logger.info(f"Generating data")
data = generative_model(30, 100, 0)
init_users, vouches, init_entities, privacy, judgments = data

logger.info(f"Running pipeline")
users = pipeline.trust_propagation(init_users, vouches)
voting_rights, entities = pipeline.voting_rights(users, init_entities, vouches, privacy)
learned_models = pipeline.preference_learning(judgments, users, entities)
scaled_models = pipeline.scaling(learned_models, users, entities, voting_rights, privacy)
rescaled_models, global_model = pipeline.aggregation(voting_rights, scaled_models, users, entities)
display_models, display_global_model = pipeline.post_process(rescaled_models, global_model, entities)

truth = entities["svd0"]
estimate = [global_model(e, row)[0] for e, row in entities.iterrows()]
correlation = np.corrcoef(truth, estimate)[0, 1]
logger.info(f"Successful run")

mehestan_models = pipeline.scaling.scalings[0](learned_models, users, entities, voting_rights,
    privacy)
mehestan_multiplicators = [mehestan_models[user].multiplicator for user in users.index]
mehestan_translations = [mehestan_models[user].translation for user in users.index]
svd0_mean = [
    entities.loc[list(learned_models[user].scored_entities(entities)), "svd0"].mean()
    for user in users.index
]
    
users = users.assign(
    mehestan_multiplicator=mehestan_multiplicators, 
    mehestan_translation=mehestan_translations,
    svd0_mean=svd0_mean
)
