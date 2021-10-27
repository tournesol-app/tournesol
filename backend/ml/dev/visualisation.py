"""
Visualisation methods, mainly for testing and debugging
"""
import random

import numpy as np
import torch

from ml.core import TOURNESOL_DEV, ML_DIR
from ml.data_utility import replace_dir
from ml.losses import round_loss
from .plots import (
    plot_metrics, plot_density, plot_s_predict_gt, plot_loc_uncerts)

if not TOURNESOL_DEV:
    raise Exception('Dev module called whereas TOURNESOL_DEV=0')


PLOTS_DIR = ML_DIR + 'plots/'
replace_dir(PLOTS_DIR)  # emply folder, create if doesn't exist


# debug helpers
def check_one(vid, comp_glob, comp_loc):
    """ prints global and local scores for one video """
    print("all we have on video: ", vid)
    for score in comp_glob:
        if score[0] == vid:
            print(score)
    for score in comp_loc:
        if score[1] == vid:
            print(score)


def seedall(seed):
    """ seeds all sources of randomness """
    reproducible = (seed >= 0)
    torch.manual_seed(seed)
    random.seed(seed)
    np.random.seed(seed)
    torch.backends.cudnn.deterministic = reproducible
    torch.backends.cudnn.benchmark = not reproducible
    print("\nSeeded all to", seed)


def disp_one_by_line(iterat):
    """ prints one iteration by line """
    for obj in iterat:
        print(obj)


def disp_fake_pred(fakes, preds):
    """ Prints gt and predictions side by side """
    print("FAKE PREDICTED")
    diff = 0
    for fake, pred in zip(fakes, preds):
        fake, pred = round(fake, 2), pred[2]
        print(fake, pred)
        diff += 100 * abs(fake - pred)**2
    print('mean dist**2 =', diff/len(preds))


def measure_diff(fakes, preds):
    """ Measures difference between ground truth and prediction

    fakes (float array): generated "true" global scores
    preds (list list): list of [video_id: int, criteria_name: str,
                                    score: float, uncertainty: float]
                            in same order

    Returns:
        (float): 100 times mean squared distance
                    between ground truth and predicted score
    """
    diff = 0
    for fake, pred in zip(fakes, preds):
        fake, pred = round(fake, 2), pred[2]
        diff += 100 * abs(fake - pred)**2
    return diff/len(preds)


def print_t(licch):
    """ Prints t stats """
    l_t = [(round_loss(t_par, 2), uid) for t_par, uid in zip(
        licch.all_nodes("t_par"),
        licch.nodes.keys()
    )]
    tens = torch.tensor(l_t)
    # disp_one_by_line(l_t)
    tens = tens[:, 0]
    print("mean of t: ", round_loss(torch.mean(tens), 2))
    print(
        "min and max of t: ",
        round_loss(torch.min(tens), 2),
        round_loss(torch.max(tens), 2)
    )
    print("var of t: ", round_loss(torch.var(tens), 2))


def print_s(licch):
    """ Prints s stats """
    l_s = [(round_loss(s_par, 2), uid) for s_par, uid in zip(
        licch.all_nodes("s_par"),
        licch.nodes.keys()
    )]
    tens = torch.tensor(l_s)
    # disp_one_by_line(l_s)
    tens = tens[:, 0]
    print("mean of s: ", round_loss(torch.mean(tens), 2))
    print(
        "min and max of s: ",
        round_loss(torch.min(tens), 2),
        round_loss(torch.max(tens), 2)
    )
    print("var of s: ", round_loss(torch.var(tens), 2))


def licch_stats(licch):
    """ gives some statistics about Licchavi object """
    print('LICCH_SATS')
    licch.check()  # some tests
    print("nb_nodes", licch.nb_nodes)
    print_t(licch)  # print stats on t parameters
    print_s(licch)  # print stats on s parameters
    with torch.no_grad():
        gen_s = licch.all_nodes("s_par")
        l_s = [s_par.item() for s_par in gen_s]
        plot_density(
            l_s,
            "s parameters",
            PLOTS_DIR,
            "s_pars.png"
        )
        gen_t = licch.all_nodes("t_par")
        l_t = [t_par.item() for t_par in gen_t]
        plot_density(
            l_t,
            "t parameters",
            PLOTS_DIR,
            "t_pars.png"
        )
    plot_metrics([licch.history_loc], path=PLOTS_DIR)
    plot_metrics([licch.history_glob], path=PLOTS_DIR)


def scores_stats(glob_scores):
    """ gives statistics on global scores

    glob_scores: torch tensor of global scores
    """
    print('SCORES_STATS')
    var = torch.var(glob_scores)
    mini, maxi = (torch.min(glob_scores).item(),
                  torch.max(glob_scores).item())
    print("minimax:", mini, maxi)
    print("variance of global scores :", var.item())
    with torch.no_grad():
        plot_density(
            glob_scores.cpu(),
            "Global scores",
            PLOTS_DIR,
            "scores.png"
        )


def s_stats(licch):
    """ Prints and plots about s parameters """
    if licch.test_mode:
        s_predicted = [s.detach().item() for s in licch.all_nodes('s_par')]
        plot_s_predict_gt(s_predicted, licch.s_gt, PLOTS_DIR)


def uncert_stats(licch, loc_uncerts):
    """ Prints and plots about uncertainty """
    l_nb_comps, l_uncerts = [], []
    vid_vidx = licch.vid_vidx
    for uncerts, node in zip(loc_uncerts, licch.nodes.values()):
        nb_comps = torch.sum(node.vid1, axis=0) + torch.sum(node.vid2, axis=0)
        for uncert, vid in zip(uncerts, node.vids):
            l_nb_comps.append(nb_comps[vid_vidx[int(vid)]].item())
            l_uncerts.append(uncert.item())
    plot_loc_uncerts(l_nb_comps, l_uncerts, PLOTS_DIR)


def output_infos(licch, glob, loc, uncertainties):
    """ Prints and plots for dev mode """
    licch_stats(licch)
    # scores_stats(glob[1])
    # s_stats(licch)
    if uncertainties[0] is not None:
        uncert_stats(licch, uncertainties[0])
