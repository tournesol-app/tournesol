from os import makedirs
import torch

from .plots import plot_metrics 
from .data_utility import save_to_json, load_from_json
from .visualisation import seedall, check_one, disp_one_by_line

"""
Not used in production, for testing only
Module called from "ml_train.py" only if env var TOURNESOL_DEV is True

Used to perform some tests on ml algorithm (custom data, ...)
"""

PATH_PLOTS = "ml/plots/"
makedirs(PATH_PLOTS, exist_ok=True)

CRITERIAS = ["reliability"]
TEST_DATA = [
                [0, 100, 101, "reliability", 100, 0],
                [0, 101, 110, "reliability", 0, 0],
                [1, 100, 101, "importance", 100, 0],
                [1, 100, 101, "reliability", 100, 0],
                [1, 102, 103, "reliability", 70, 0],
                [2, 104, 105, "reliability", 50, 0],
                [3, 106, 107, "reliability", 30, 0],
                [4, 108, 109, "reliability", 30, 0],
                # [67, 200, 201, "reliability", 0, 0]
            ] #+ [[0, 555, 556, "reliability", 40, 0]] * 10 

NAME = ""
EPOCHS = 50
TRAIN = True 
RESUME = True

def run_experiment(comparison_data):
    """ trains and outputs some stats """
    if TRAIN:
        seedall(4)
        from .ml_train import ml_run
        glob_scores, contributor_scores = ml_run(comparison_data[:10000], 
                                                    EPOCHS,
                                                    CRITERIAS, 
                                                    RESUME,
                                                    verb=1)
        save_to_json(glob_scores, contributor_scores, NAME)
    else:
        glob_scores, contributor_scores = load_from_json(NAME)
    for c in contributor_scores:
        if c[0]==6213:
            print(c)
    disp_one_by_line(glob_scores[:10])
    disp_one_by_line(contributor_scores[:10])
    check_one(100, glob_scores, contributor_scores)
    print("glob:", len(glob_scores), "local:",  len(contributor_scores))

def licch_stats(licch):
    ''' gives some statistics about licchavi object '''
    licch.check() # some tests
    h = licch.history
    print("nb_nodes", licch.nb_nodes)
    licch.stat_s()  # print stats on s parameters
    plot_metrics([h], path=PATH_PLOTS)

def scores_stats(glob_scores):
    ''' gives statistics on global scores
    
    glob_scores: torch tensor of global scores
    '''
    var = torch.var(glob_scores)
    mini, maxi = (torch.min(glob_scores).item(),  
                torch.max(glob_scores).item() )
    print("minimax:", mini,maxi)
    print("variance of global scores :", var.item())
