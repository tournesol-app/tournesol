import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from solidago import *
from solidago.primitives.timer import time


logger = logging.getLogger(__name__)

with time("Retrieve public dataset", logger):
    t = TournesolExport.download()

t = poll_functions.Filtering(criteria="largely_recommended")(t)
criteria = t.criteria()
pipeline = poll_functions.TournesolFull()
assert isinstance(pipeline.aggregate, poll_functions.EntitywiseQrQuantile)

with time("Full Tournesol pipeline", logger):
    t = pipeline(t)

# Filtering over entities with sufficiently many comparisons and evaluators
t.entities = Entities(t.entities.df[t.entities.df["n_comparisons"] >= 100 & t.entities.df["n_evaluators"] >= 20])
t.user_models.user_directs = t.user_models.user_directs.filters(entity_name=list(t.entities.names()))
t.global_model.directs = t.global_model.directs.filters(entity_name=list(t.entities.names()))
assert t.global_model.directs.keys("entity_name") == t.entities.names()

quantiles = [0.1, 0.2, 0.35, 0.5, 0.65, 0.8, 0.9]

polls: list[Poll] = list()
for q in quantiles:
    pipeline.aggregate.quantile = q
    p = pipeline.post_process(pipeline.aggregate(t))
    p.global_model.directs.set_columns(rank=list(np.argsort(p.global_model.directs.value)))
    for score in p.global_model.directs:
        entity = p.entities[score["entity_name"]]
        assert isinstance(entity, Entity)
        entity["rank"] = score["rank"]
    t.entities.set_column(f"value_q={q}", p.global_model.directs.value)
    t.entities.set_column(f"rank_q={q}", p.entities.get_column("rank"))
    
t.entities.assign(
    value_delta = t.entities.get_column("value_q=0.8").to_numpy(np.float64) - t.entities.get_column("value_q=0.2"),
    rank_delta = t.entities.get_column("rank_q=0.8").to_numpy(np.float64) - t.entities.get_column("rank_q=0.2")
)

extreme_values = set(t.entities.df.sort_values("value_delta")[:5].video) 
extreme_values |= set(t.entities.df.sort_values("value_delta")[-5:].video)
extreme_ranks = set(t.entities.df.sort_values("rank_delta")[:5].video) 
extreme_ranks |= set(t.entities.df.sort_values("rank_delta")[-5:].video)
