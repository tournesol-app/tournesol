import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from threading import Thread

from solidago.pipeline.inputs import TournesolDataset

from solidago.trust_propagation import LipschiTrust
from solidago.voting_rights import AffineOvertrust
from solidago.preference_learning import UniformGBT
from solidago.scaling import ScalingCompose, Mehestan, QuantileZeroShift
from solidago.aggregation import StandardizedQrQuantile
from solidago.post_process import Squash
from solidago.pipeline import Pipeline


logger = logging.getLogger(__name__)

info_loggers = [
    __name__, 
    "solidago.pipeline.pipeline", 
    "solidago.scaling.mehestan",
    "solidago.preference_learning.base"
]
for module in info_loggers:
    info_logger = logging.getLogger(module)
    info_logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    info_logger.addHandler(ch)

logger.info("Retrieve public dataset")
inputs = TournesolDataset.download()
video_id_to_entity_id = { 
    video_id: entity_id 
    for entity_id, video_id in enumerate(inputs.entity_id_to_video_id)
}


# criteria = set(inputs.comparisons["criteria"])
criteria = { "largely_recommended" }

pipeline = Pipeline(
    trust_propagation=LipschiTrust(
        pretrust_value=0.8,
        decay=0.8,
        sink_vouch=5.0,
        error=1e-8
    ),
    voting_rights=AffineOvertrust(
        privacy_penalty=0.5, 
        min_overtrust=2.0,
        overtrust_ratio=0.1,
    ),
    preference_learning=UniformGBT(
        prior_std_dev=7,
        convergence_error=1e-5,
        cumulant_generating_function_error=1e-5,
    ),
    scaling=ScalingCompose(
        Mehestan(
            lipschitz=0.1,
            min_activity=10,
            n_scalers_max=500,
            privacy_penalty=0.5,
            p_norm_for_multiplicative_resilience=4.0,
            error=1e-5
        ),
        QuantileZeroShift(
            zero_quantile=0.15,
            lipschitz=0.1,
            error=1e-5
        )
    ),
    aggregation=StandardizedQrQuantile(
        quantile=0.2,
        dev_quantile=0.9,
        lipschitz=100,
        error=1e-5
    ),
    post_process= Squash(
        score_max=100
    )
)

user_outputs, entities, voting_rights, scaled_user_models = dict(), dict(), dict(), dict()

    
for c in criteria:
    logger.info(f"Running the pipeline for criterion `{c}`")

    pipeline_objects = inputs.get_pipeline_kwargs(criterion=c)
    users = pipeline_objects["users"]
    vouches = pipeline_objects["vouches"]
    all_entities = pipeline_objects["entities"]
    privacy = pipeline_objects["privacy"]
    judgments = pipeline_objects["judgments"]

    users = pipeline.trust_propagation(users, vouches)
    voting_rights[c], entities[c] = pipeline.voting_rights(users, all_entities, vouches, privacy)
    user_models = pipeline.preference_learning(judgments, users, entities[c])
    scaled_user_models[c] = pipeline.scaling(user_models, users, entities[c], voting_rights[c], privacy)

# threads = [Thread(target=run_pipeline, args=(criterion,)) for criterion in criteria]
# for thread in threads:
#     thread.start()
# for thread in threads:
#     thread.join()

logger.info(f"Successful pipeline run.")    

scores = inputs.collective_scores

squashed_user_models, global_model = dict(), dict()
quantiles = [0.1, 0.2, 0.35, 0.5, 0.65, 0.8, 0.9]

for q in quantiles:
    
    pipeline.aggregation.quantile = q
    squashed_user_models[q], global_model[q] = dict(), dict()
    for c in criteria:
        user_models, global_model[q][c] = pipeline.aggregation(voting_rights[c], scaled_user_models[c], users, entities[c])
        squashed_user_models[q][c], global_model[q][c] = pipeline.post_process(user_models, global_model[q][c], entities)
    
    q_scores = list()
    for _, row in scores.iterrows():
        try:
            entity_id = video_id_to_entity_id[row.video]
            q_scores.append(global_model[q][row.criteria](entity_id, None)[0])
        except:
            q_scores.append(0.)
    scores[f"score_q={q}"] = q_scores

comparisons = inputs.comparisons
s_main = scores[scores.criteria == "largely_recommended"]
c_main = comparisons[comparisons.criteria == "largely_recommended"]

entity_a_counts = c_main.value_counts("entity_a")
entity_b_counts = c_main.value_counts("entity_b")

def n_comparisons(video):
    total = 0
    if video not in video_id_to_entity_id:
        return 0
    if video_id_to_entity_id[video] in entity_a_counts:
        total += entity_a_counts[video_id_to_entity_id[video]]
    if video_id_to_entity_id[video] in entity_b_counts:
        total += entity_b_counts[video_id_to_entity_id[video]]
    return total

def n_contributors(video):
    if video not in video_id_to_entity_id:
        return 0
    entity = video_id_to_entity_id[video]
    contributors = set(c_main[c_main.entity_a == entity].user_id)
    contributors |= set(c_main[c_main.entity_b == entity].user_id)
    return len(contributors)

s_main.loc[:,"n_comparisons"] = [n_comparisons(r.video) for _, r in s_main.iterrows()]
s_main.loc[:,"n_contributors"] = [n_contributors(r.video) for _, r in s_main.iterrows()]

s_top_main = s_main[(s_main.n_comparisons > 100) & (s_main.n_contributors > 20)]
top_entities = set(s_top_main.video)
c_top_main = c_main[(c_main.entity_a.isin(top_entities)) | (c_main.entity_b.isin(top_entities))]


ranking = { q: s_top_main.sort_values(f"score_q={q}", ascending=False)["video"] for q in quantiles }
for q in quantiles:
    rk = list(ranking[q])
    s_top_main.loc[:, f"ranking_q={q}"] = [ rk.index(r.video) for _, r in s_top_main.iterrows() ]

ranking_cols = [f"ranking_q={q}" for q in quantiles]

s_top_main.loc[:, "ranking_delta"] = s_top_main["ranking_q=0.8"] - s_top_main["ranking_q=0.2"]
s_top_main.loc[:, "score_delta"] = s_top_main["ranking_q=0.8"] - s_top_main["ranking_q=0.2"]

largest_delta = set(s_top_main.sort_values("score_delta")[:5].video) 
largest_delta |= set(s_top_main.sort_values("score_delta")[-5:].video)

s_plot = s_top_main[s_top_main.video.isin(largest_delta)][["video"] + ranking_cols].set_index("video")


