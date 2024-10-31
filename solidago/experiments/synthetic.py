import sys
import json
import os
import logging
import numpy as np
import pandas as pd

from threading import Thread

from solidago.privacy_settings import PrivacySettings
from solidago.judgments import Judgments, DataFrameJudgments
from solidago.scoring_model import (
    ScoringModel, DirectScoringModel, ScaledScoringModel, PostProcessedScoringModel
)

from solidago.generative_model import GenerativeModel
from solidago.pipeline import Pipeline

from plot import plot, plot_file

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logger.addHandler(ch)


def sample_correlation(n_users, n_entities, seed, generative_model, pipeline) -> float:
    data = generative_model(n_users, n_entities, seed)
    init_users, vouches, entities, privacy, judgments = data
    users, voting_rights, user_models, global_model = pipeline(*data)
    
    truth = entities["svd0"]
    estimate = [
        global_model(e, row)[0] if global_model(e, row) is not None else 0.
        for e, row in entities.iterrows()
    ]
    return np.corrcoef(truth, estimate)[0, 1]
    
def sample_n_correlations(n_users, n_entities, n_seeds, generative_model, pipeline, thread=False):
    if not thread:
        return [
            sample_correlation(n_users, n_entities, seed, generative_model, pipeline) 
            for seed in range(n_seeds)
        ]
    results = [None] * n_seeds
    def r(seed):
        results[seed] = sample_correlation(n_users, n_entities, seed, generative_model, pipeline)
    threads = [Thread(target=r, args=(seed,)) for seed in range(n_seeds)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    return results

def set_attr(x_parameter: str, x: float, generative_model, pipeline):
    x_list = x_parameter.split(".")
    
    if x_list[0] == "generative_model": 
        obj = generative_model
    elif x_list[0] == "pipeline":
        obj = pipeline
    else: 
        raise ValueError(f"No match for {x_parameter[0]}")
        
    for attr in x_list[1:-1]:
        try:    obj = getattr(obj, attr)
        except: 
            try: obj = obj[attr]
            except: obj = obj[int(attr)]
    try:
        setattr(obj, x_list[-1], x)
    except:
        obj[x_list[-1]] = x
    
def get_attr(x_parameter: str, generative_model, pipeline):
    x_list = x_parameter.split(".")
    
    if x_list[0] == "generative_model": 
        obj = generative_model
    elif x_list[0] == "pipeline":
        obj = pipeline
    else: 
        raise ValueError(f"No match for {x_parameter[0]}")
    
    for attr in x_list[1:]:
        try:    obj = getattr(obj, attr)
        except: 
            try: obj = obj[attr]
            except: obj = obj[int(attr)]
        
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
    assert filename[-5:] == ".json", "json files only"
    assert os.path.exists(filename), f"File {filename} does not exist"
    
    filename_list = filename.split("/")
    results_directory = filename_list[:-1]
    results_directory.append("results")
    results_directory = "/".join(results_directory)
    if not os.path.exists(results_directory):
        os.mkdir(results_directory)
    results_filename = results_directory + f"/{filename_list[-1]}"
    
    experiment_number, base_results_filename = 0, results_filename
    while os.path.exists(results_filename):
        experiment_number += 1
        results_filename = base_results_filename[:-5] + f"_{experiment_number}.json"
    
    with open(filename) as json_file:
        hps = json.load(json_file)
    
    logger.info(f"Running experiment with hyperparameters {filename}")
    generative_model = GenerativeModel.from_json(hps["generative_model"])
    pipeline = Pipeline.from_json(hps["pipeline"])
    hps["yvalues"] = run_experiment(hps["n_users"], hps["n_entities"], hps["n_seeds"],
        hps["xparameter"], hps["xvalues"], hps["zparameter"], hps["zvalues"],
        generative_model, pipeline)
    
    with open(results_filename, "w") as results_file:
        json.dump(hps, results_file)
    logger.info(f"The experiment results were successfully exported in file {filename}")
    
    plot_filename = results_filename[:-5] + ".pdf"
    plot(hps, plot_filename)
    logger.info(f"The results were plotted in file {plot_filename}")


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
