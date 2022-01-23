import random

import numpy as np
import torch

from ml.data_utility import replace_dir

from .plots import plot_density, plot_loc_uncerts, plot_metrics, plot_s_predict_gt

"""
Visualisation methods, mainly for testing and debugging

Main file is "ml_train.py"
"""

PATH_PLOTS = "ml/plots/"
replace_dir(PATH_PLOTS)  # emply folder, create if doesn't exist


# debug helpers
def check_one(vid, comp_glob, comp_loc):
    """prints global and local scores for one video"""
    print("all we have on video: ", vid)
    for score in comp_glob:
        if score[0] == vid:
            print(score)
    for score in comp_loc:
        if score[1] == vid:
            print(score)


def seedall(s):
    """seeds all sources of randomness"""
    reproducible = s >= 0
    torch.manual_seed(s)
    random.seed(s)
    np.random.seed(s)
    torch.backends.cudnn.deterministic = reproducible
    torch.backends.cudnn.benchmark = not reproducible
    print("\nSeeded all to", s)


def disp_one_by_line(it):
    """prints one iteration by line"""
    for obj in it:
        print(obj)


def disp_fake_pred(fakes, preds):
    print("FAKE PREDICTED")
    diff = 0
    for fake, pred in zip(fakes, preds):
        f, p = round(fake, 2), pred[2]
        print(f, p)
        diff += 100 * abs(f - p) ** 2
    print("mean dist**2 =", diff / len(preds))


def measure_diff(fakes, preds):
    """Measures difference between ground truth and prediction

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
        f, p = round(fake, 2), pred[2]
        diff += 100 * abs(f - p) ** 2
    return diff / len(preds)


def licch_stats(licch):
    """gives some statistics about Licchavi object"""
    print("LICCH_SATS")
    licch.check()  # some tests
    h = licch.history
    print("nb_nodes", licch.nb_nodes)
    licch.stat_s()  # print stats on s parameters
    with torch.no_grad():
        gen_s = licch.all_nodes("s")
        l_s = [s.item() for s in gen_s]
        plot_density(l_s, "s parameters", PATH_PLOTS, "s_params.png")
    plot_metrics([h], path=PATH_PLOTS)


def scores_stats(glob_scores):
    """gives statistics on global scores

    glob_scores: torch tensor of global scores
    """
    print("SCORES_STATS")
    var = torch.var(glob_scores)
    mini, maxi = (torch.min(glob_scores).item(), torch.max(glob_scores).item())
    print("minimax:", mini, maxi)
    print("variance of global scores :", var.item())
    with torch.no_grad():
        plot_density(
            glob_scores.cpu(),
            "Global scores",
            PATH_PLOTS,
            "scores.png"
        )


def s_stats(licch):
    """ Prints and plots about s parameters """
    if licch.test_mode:
        s_predicted = [s.detach().item() for s in licch.all_nodes('s')]
        plot_s_predict_gt(s_predicted, licch.s_gt, PATH_PLOTS)


def uncert_stats(licch, loc_uncerts):
    """ Prints and plots about uncertainty """
    l_nb_comps, l_uncerts = [], []
    vid_vidx = licch.vid_vidx
    for uncerts, node in zip(loc_uncerts, licch.nodes.values()):
        nb_comps = torch.sum(node.vid1, axis=0) + torch.sum(node.vid2, axis=0)
        for uncert, vid in zip(uncerts, node.vids):
            l_nb_comps.append(nb_comps[vid_vidx[int(vid)]].item())
            l_uncerts.append(uncert)
    plot_loc_uncerts(l_nb_comps, l_uncerts, PATH_PLOTS)


def output_infos(licch, glob, loc, uncertainties):
    """ Prints and plots for dev mode """
    licch_stats(licch)
    scores_stats(glob[1])
    s_stats(licch)
    if uncertainties[1] is not None:
        uncert_stats(licch, uncertainties[1])
