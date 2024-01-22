import sys
import json
import os

import logging
import numpy as np
import pandas as pd

from solidago.privacy_settings import PrivacySettings
from solidago.judgments import Judgments, DataFrameJudgments
from solidago.scoring_model import (
    ScoringModel, DirectScoringModel, ScaledScoringModel, PostProcessedScoringModel
)

from solidago.generative_model import GenerativeModel
from solidago.generative_model.user_model import UserModel, NormalUserModel
from solidago.generative_model.vouch_model import VouchModel, ErdosRenyiVouchModel
from solidago.generative_model.entity_model import EntityModel, NormalEntityModel
from solidago.generative_model.engagement_model import EngagementModel, SimpleEngagementModel
from solidago.generative_model.comparison_model import ComparisonModel, KnaryGBT

from solidago.pipeline import Pipeline
from solidago.trust_propagation import TrustPropagation, LipschiTrust
from solidago.voting_rights import VotingRights, VotingRightsAssignment, AffineOvertrust
from solidago.preference_learning import PreferenceLearning, UniformGBT
from solidago.scaling import Scaling, ScalingCompose, Mehestan, QuantileZeroShift
from solidago.aggregation import Aggregation, QuantileStandardizedQrMedian
from solidago.post_process import PostProcess, Squash

logger = logging.getLogger(__name__)

    
generative_model = GenerativeModel(
    user_model=NormalUserModel(
        p_trustworthy= 0.8,
        p_pretrusted= 0.2,
        zipf_vouch= 2.0,
        zipf_compare= 1.5,
        poisson_compare= 30.0,
        n_comparisons_per_entity=3.0,
        svd_dimension=5,
    ),
    vouch_model=ErdosRenyiVouchModel(),
    entity_model=NormalEntityModel(
        svd_dimension=5,
    ),
    engagement_model=SimpleEngagementModel(
        p_per_criterion={"0": 1.0}, 
        p_private=0.2
    ),
    comparison_model=KnaryGBT(n_options=21, comparison_max=10)
)
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
            lipschitz=1,
            min_activity=1,
            n_scalers_max=100,
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
    aggregation=QuantileStandardizedQrMedian(
        dev_quantile=0.9,
        lipschitz=0.1,
        error=1e-5
    ),
    post_process=Squash(
        score_max=100
    )
)

def sample_correlation(n_users, n_entities, seed, generative_model, pipeline) -> float:
    data = generative_model(n_users, n_entities, seed)
    init_users, vouches, entities, privacy, judgments = data
    users, voting_rights, user_models, global_model = pipeline(*data)
    
    svd_dim, svd_cols = 0, list()
    while f"svd{svd_dim}" in entities:
        svd_cols.append(f"svd{svd_dim}")
        svd_dim += 1
    
    truth = entities[svd_cols].sum(axis=1)
    estimate = [global_model(e, row)[0] for e, row in entities.iterrows()]
    return np.corrcoef(truth, estimate)[0, 1]
    
def sample_n_correlations(n_users, n_entities, n_seeds, generative_model, pipeline):
    return [
        sample_correlation(n_users, n_entities, seed, generative_model, pipeline) 
        for seed in range(n_seeds)
    ]

def set_attr(x_parameter: str, x: float, generative_model, pipeline):
    x_list = x_parameter.split(".")
    
    match x_list[0]:
        case "generative_model": obj = generative_model
        case "pipeline":         obj = pipeline
        case _: raise ValueError(f"No match for {x_parameter[0]}")
        
    for attr in x_list[1:-1]:
        try:    obj = getattr(obj, attr)
        except: obj = obj[attr]
    try:
        setattr(obj, x_list[-1], x)
    except:
        obj[x_list[-1]] = x
    
def get_attr(x_parameter: str, generative_model, pipeline):
    x_list = x_parameter.split(".")
    
    match x_list[0]:
        case "generative_model": obj = generative_model
        case "pipeline":         obj = pipeline
        case _: raise ValueError(f"No match for {x_parameter[0]}")
    
    for attr in x_list[1:]:
        try:    obj = getattr(obj, attr)
        except: obj = obj[attr]
        
    return obj
        
def run_experiment(
    n_users: int, 
    n_entities: int,
    n_seeds: int, 
    x_parameter: str, 
    x_values: list[float], 
    z_parameter: str, 
    z_values: list[float],
    generative_model, 
    pipeline
):
    """ Run experiments with multiple seeds. Outputs results in json.
    
    Parameters
    ----------
    n_users: int
    n_entities: int
    n_seeds: int
        For reproducibility and variance estimation.
    x_parameter: str
        path towards parameter, e.g. "generative_model.user_model.p_trustworthy"
    x_values: list[float]
        list of changed values for this attribute
    z_parameter: tuple[str]
        path towards parameter, e.g. "pipeline.aggregation.lipschitz"
    z_values: list[float]
        list of changed values for this attribute        
    
    Returns
    -------
    json: dict[str, list[list[list[float]]]]
        json["generative_model"] describes the base generative model
        json["pipeline"] describes the base pipeline
        json["results"][z_value][x_value][seed] is the score of the output.
    """
    results = list()
    for z in z_values:
        z_results = list()
        set_attr(z_parameter, z, generative_model, pipeline)
        logger.info(f"Running experiments for {z_parameter} = {z}")
        for x in x_values:
            set_attr(x_parameter, x, generative_model, pipeline)
            logger.info(f"    {x_parameter} = {x}")
            c = sample_n_correlations(n_users, n_entities, n_seeds, generative_model, pipeline)
            z_results.append(c)
        results.append(z_results)
    return results

def run_from_hyperparameters_file(filename):
    
    if filename[-5:] != ".json":
        filename += ".json"
    
    assert os.path.exists(filename), f"File {filename} does not exist"
    
    filename_list = filename.split("/")
    results_directory = "/".join(filename_list[:-1]) + "/results"
    if not os.path.exists(results_directory):
        os.mkdir(results_directory)
    results_filename = results_directory + f"/{filename_list[-1]}"
    
    experiment_number = 0
    while os.path.exists(results_filename):
        experiment_number += 1
        results_filename = results_filename[:-5] + f"_{experiment_number}.json"
    
    with open(filename) as json_file:
        hps = json.load(json_file)
    
    logger.info(f"Running experiment with hyperparameters {filename}")
    generative_model = GenerativeModel.from_json(hps["generative_model"])
    pipeline = Pipeline.from_json(hps["pipeline"])
    hps["results"] = run_experiment(hps["n_users"], hps["n_entities"], hps["n_seeds"],
        hps["x_parameter"], hps["x_values"], hps["z_parameter"], hps["z_values"],
        generative_model, pipeline)
    
    with open(results_filename, "w") as results_file:
        json.dump(hps, results_file)
    logger.info(f"The experiment results were successfully exported in file {filename}")


if len(sys.argv) == 1:
    logger.warn("Please specify the hyperparameters of the pipeline experiments in a json file.")
    logger.warn("The file must specify n_users, n_entities, n_seeds, x_parameter, x_values,")
    logger.warn("z_parameter, z_values. See `experiments/hyperparameters.json` for an example.")
    logger.warn("You may then add the filename of the json hyperparameters file.")

elif sys.argv[1] == "plot":
    from plot import plot_file
    plot_file(sys.argv[2])
    
else:
    run_from_hyperparameters_file(sys.argv[1])
