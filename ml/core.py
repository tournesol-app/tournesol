import os
import logging
from time import time
import gin

from ml.licchavi import Licchavi
from ml.handle_data import (
    select_criteria, shape_data, distribute_data,
    distribute_data_from_save, format_out_loc, format_out_glob)
from ml.dev.visualisation import (licch_stats, scores_stats, s_stats, 
                                  uncert_stats)

TOURNESOL_DEV = bool(int(os.environ.get("TOURNESOL_DEV", 0)))  # dev mode
FOLDER_PATH = "ml/checkpoints/"
FILENAME = "models_weights"
PATH = FOLDER_PATH + FILENAME
os.makedirs(FOLDER_PATH, exist_ok=True)
logging.basicConfig(filename='ml/ml_logs.log', level=logging.INFO)


def _set_licchavi(
        comparison_data, criteria,
        fullpath=None, resume=False,
        verb=2, device='cpu',
        ground_truths=None):
    ''' Shapes data and inputs it in Licchavi to initialize

    comparison_data (list of lists): output of fetch_data()
    criteria (str): rating criteria
    fullpath (str): path from which to load previous training
    resume (bool): wether to resume previous training or not
    verb (int): verbosity level
    device (str): device used (cpu/gpu)
    ground_truths (float array, couples list list): global and local ground
                                                    truths (generated scores)

    Returns :
        (Licchavi()): Licchavi object initialized with data
        (int array): array of users IDs in order
    '''
    # shape data
    one_crit_data = select_criteria(comparison_data, criteria)
    full_data = shape_data(one_crit_data)
    test_mode = ground_truths is not None
    # set licchavi using data
    if resume:
        nodes_dic, users_ids, vid_vidx = distribute_data_from_save(full_data,
                                                                   fullpath,
                                                                   device)
        licch = Licchavi(
            len(vid_vidx), vid_vidx, criteria,
            test_mode, device, verb
        )
        licch.load_and_update(nodes_dic, users_ids, fullpath)
    else:
        nodes_dic, users_ids, vid_vidx = distribute_data(full_data, device)
        licch = Licchavi(
            len(vid_vidx), vid_vidx, criteria,
            test_mode, device, verb
        )
        licch.set_allnodes(nodes_dic, users_ids)
    if test_mode:
        licch.set_ground_truths(*ground_truths)
    return licch, users_ids  # FIXME we can do without users_ids ?


def _train_predict(
        licch, epochs,
        fullpath=None, save=False, verb=2, compute_uncertainty=False):
    ''' Trains models and returns video scores for one criteria

    licch (Licchavi()): licchavi object innitialized with data
    epochs (int): maximum number of training epochs
    fullpath (str): path where to save trained models
    save (bool): wether to save the result of training or not
    verb (int): verbosity level

    Returns :
    - (list of all vIDS , tensor of global video scores)
    - (list of arrays of local vIDs , list of tensors of local video scores)
    (float list list, float list): uncertainty of local scores, 
                                    uncertainty of global scores
                                    (None, None) if not computed
    '''
    uncertainties = licch.train(
        epochs,
        compute_uncertainty=compute_uncertainty)
    glob, loc = licch.output_scores()
    if save:
        licch.save_models(fullpath)
    if TOURNESOL_DEV:  # some prints and plots
        licch_stats(licch)
        scores_stats(glob[1])
        s_stats(licch)
        if uncertainties[1] is not None:
            uncert_stats(licch, uncertainties[1])
    return glob, loc, uncertainties


@gin.configurable
def ml_run(
        comparison_data, epochs, criterias,
        resume=False, save=True, verb=1, device='cpu',
        ground_truths=None, compute_uncertainty=False):
    """ Runs the ml algorithm for all criterias

    comparison_data (list of lists): output of fetch_data()
    epochs (int): number of epochs of gradient descent for Licchavi
    criterias (str list): list of criterias to compute
    resume (bool): wether to resume from save or not
    save (bool): wether to save result of training or not
    verb (int): verbosity level
    device (str): device used (cpu/gpu)

    Returns:
    - video_scores: list of [video_id: int, criteria_name: str,
                                score: float, uncertainty: float]
    - contributor_rating_scores: list o
    [   contributor_id: int, video_id: int, criteria_name: str,
        score: float, uncertainty: float]
    """  # FIXME: not better to regroup contributors in same list or smthg ?
    ml_run_time = time()
    glob_scores, loc_scores = [], []

    for criteria in criterias:
        logging.info("PROCESSING " + criteria)
        fullpath = PATH + '_' + criteria

        # preparing data
        licch, users_ids = _set_licchavi(
            comparison_data, criteria,
            fullpath, resume, verb, device,
            ground_truths
        )
        # training and predicting
        glob, loc, uncertainties = _train_predict(
            licch, epochs, fullpath, save, verb,
            compute_uncertainty=compute_uncertainty
        )
        # putting in required shape for output
        out_glob = format_out_glob(glob, criteria, uncertainties[0])
        out_loc = format_out_loc(loc, users_ids, criteria, uncertainties[1])
        glob_scores += out_glob
        loc_scores += out_loc

    logging.info(f'ml_run() total time : {round(time() - ml_run_time)}')
    return glob_scores, loc_scores


# parse parameters written in "hyperparameters.gin"
gin.parse_config_file('ml/hyperparameters.gin')
