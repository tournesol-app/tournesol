"""
Metrics used for training monitoring in "licchavi.py"
"""
import logging
from statistics import median
from copy import deepcopy

import torch
from torch.autograd.functional import hessian

from .losses import (
    loss_s_gen_reg, round_loss, loss_fit, models_dist_huber,
    model_norm, models_dist)


# metrics on models
def scalar_product(l_grad1, l_grad2):
    """ scalar product of 2 lists of gradients

    l_grad1 (float tensor list): list of gradients of a model
    l_grad2 (float tensor list): list of gradients of a model

    Returns:
        (float): scalar product of the gradients
    """
    scalar_prod = 0
    if l_grad1 is not None:
        for grad1, grad2 in zip(l_grad1, l_grad2):
            scalar_prod += (grad1 * grad2).sum()
    return round_loss(scalar_prod, 4)


def replace_coordinate(tens, score, idx):
    """ Replaces one coordinate of the tensor

    Args:
        tens (float tensor): local model
        score (scalar tensor): score to put in tens
        idx (int): index of score to replace

    Returns:
        (float tensor): same tensor as input but backward pointing to -score
    """
    size = len(tens)
    left, _, right = torch.split(tens, [idx, 1, size - idx - 1])
    return torch.cat([left, score, right])


# ------ Licchavi history computation -----------

# norms
def _metric_norm_loc(licch, args):
    """ Returns l2 norm of local scores """
    norm = 0
    with torch.no_grad():
        for node in licch.nodes.values():
            norm += model_norm(node.model, powers=(2, 0.5))
    return norm


# gradients
def _metric_grad_loc(licch, args):
    """ Norm of local model gradients """
    norm = 0
    for node in licch.nodes.values():
        norm += torch.sum(node.model.grad**2)
    return torch.sqrt(norm).item()


def _metric_grad_t(licch, args):
    """ Norm of t parameters gradients """
    norm = 0
    for node in licch.nodes.values():
        norm += node.t_par.grad**2
    return torch.sqrt(norm).item()


def _metric_grad_s(licch, args):
    """ Norm of s parameters gradients """
    norm = 0
    for node in licch.nodes.values():
        norm += node.s_par.grad**2
    return torch.sqrt(norm).item()


def _metric_grad_sp_glob(licch, args):
    """ Returns scalar product of gradients between last and current epoch """
    grad_gen = licch.global_model.grad
    if args[4] > 1:  # no previous model for first epoch
        scal_grad = scalar_product(licch.last_epoch_glob['grad_sp'], grad_gen)
    else:
        scal_grad = 0  # default value for first epoch
    licch.last_epoch_glob['grad_sp'] = deepcopy(licch.global_model.grad)
    return scal_grad


# differences
def _metric_diff_glob(licch, args):
    """ Global scores variation between 2 epochs """
    with torch.no_grad():
        if args[4] > 1:
            diff_glob = models_dist(
                licch.last_epoch_glob['diff_glob'],
                licch.global_model,
                powers=(2, 0.5)
            )
        else:
            diff_glob = 0
        licch.last_epoch_glob['diff_glob'] = deepcopy(licch.global_model)
    return diff_glob


def _metric_diff_loc(licch, args):
    """ Local scores variation between 2 epochs """
    with torch.no_grad():
        diff_loc = 0
        if args[4] > 1:
            for uidx, node in enumerate(licch.nodes.values()):
                diff_loc += models_dist(
                    licch.last_epoch_loc['diff_loc'][uidx],
                    node.model,
                    powers=(2, 0.5),
                    mask=node.mask
                )
        licch.last_epoch_loc['diff_loc'] = deepcopy(
            list(licch.all_nodes('model'))
        )
    return diff_loc


def _metric_diff_s(licch, args):
    """ s parameters variation between 2 epochs """
    with torch.no_grad():
        diff_s = torch.zeros(1)
        if args[4] > 1:
            for uidx, node in enumerate(licch.nodes.values()):
                diff_s += (
                    licch.last_epoch_glob['diff_s'][uidx] - node.s_par
                )**2
        licch.last_epoch_glob['diff_s'] = deepcopy(
            list(licch.all_nodes('s_par'))
        )
    return torch.sqrt(diff_s).item()


# test mode
def _metric_error_glob(licch, args):
    """ Error between predicted and ground truths (dev mode only) """
    with torch.no_grad():
        glob_out, _ = licch.output_scores()
        if len(glob_out[1]) != len(licch.glob_gt):
            logging.error('Some videos have not been rated')
        glob_errors = (glob_out[1] - licch.glob_gt)**2
        glob_mean_error = float(sum(glob_errors)) / licch.nb_vids
    return glob_mean_error


def _metric_error_loc(licch, args):
    """ Error between predicted and ground truths (dev mode only) """
    loc_error, nb_loc = 0, 0
    _, loc_out = licch.output_scores()
    for uid, predictions in zip(licch.nodes, loc_out[1]):
        for i, score_pred in zip(licch.loc_gt[int(uid)], predictions):
            score_gt = licch.loc_gt[int(uid)][i]
            loc_error += float((score_pred - score_gt)**2)
            nb_loc += 1
    loc_mean_error = loc_error / nb_loc
    return loc_mean_error


METRICS_FUNCS = {
    # losse terms
    'loss_fit': lambda licch, args: round_loss(args[0]),
    'loss_s': lambda licch, args: round_loss(args[1]),
    'loss_gen': lambda licch, args: round_loss(args[2]),
    'loss_reg': lambda licch, args: round_loss(args[3]),
    # norms
    'norm_glob': lambda licch, args:
        round_loss(model_norm(licch.global_model, powers=(2, 0.5)), 3),
    'norm_loc': _metric_norm_loc,
    # gradients
    'grad_glob': lambda licch, args:
        scalar_product(licch.global_model.grad, licch.global_model.grad),
    'grad_loc': _metric_grad_loc,
    'grad_t': _metric_grad_t,
    'grad_s': _metric_grad_s,
    'grad_sp_glob': _metric_grad_sp_glob,
    # differences
    'diff_loc': _metric_diff_loc,
    'diff_glob': _metric_diff_glob,
    'diff_s': _metric_diff_s,
    # test mode only, distance to ground truths
    'error_glob': _metric_error_glob,
    'error_loc': _metric_error_loc
}


def update_hist(licch, local_epoch, args):
    """ Updates Licchavi history for all metrics asked

    local_epoch (bool): True for local training, False for global
    args (tuple): losses and current epoch number
    """
    if local_epoch:  # FIXME smarter division
        for metric in licch.history_loc:
            licch.history_loc[metric].append(
                METRICS_FUNCS[metric](licch, args)
            )
    else:
        for metric in licch.history_glob:
            licch.history_glob[metric].append(
                METRICS_FUNCS[metric](licch, args)
            )


# ------ to compute uncertainty -------
def _global_uncert(values, prior=4, weight=5):
    """ Returns posterior value of median

    prior(float): value of prior median
    weight (int): weight of prior
    values (float list): data to take median of

    Returns:
        (float): global uncertainty for one video
    """
    full_values = values + [prior] * weight
    return median(full_values) / len(values)**0.5


def get_uncertainty_glob(licch):
    """ Returns uncertainty for all global scores

    Args:
        licch (Licchavi()): licchavi object

    Returns:
        (float tensor): uncertainty for all global scores
    """
    with torch.no_grad():
        uncerts = torch.empty(licch.nb_vids)  # all global uncertainties
        all_vids = list(licch.vid_vidx.keys())  # all video IDs
        for vidx in range(licch.nb_vids):  # for each video
            distances = []
            for node in licch.nodes.values():
                if all_vids[vidx] in node.vids:
                    dist = models_dist_huber(node.model, licch.global_model,
                                             vidx=vidx, strength=node.delta_na)
                    distances.append(dist.item())
            uncerts[vidx] = _global_uncert(distances)
    return uncerts


def _get_hessian_fun_loc(licch, uid, vidx):
    """ Gives loss in function of local model for hessian computation

    Args:
        licch (Licchavi()): licchavi object
        id_node (int): id of user
        vidx (int): index of video, ie index of parameter

    Returns:
        (scalar tensor -> float) function giving loss according to one score
    """
    def get_loss(score):
        """ Used to compute its second derivative to get uncertainty

        input (float scalar tensor): one score

        Returns:
            (float scalar tensor): partial loss for 1 user, 1 video
        """
        new_model = replace_coordinate(licch.nodes[uid].model, score, vidx)
        licch.nodes[uid].model = new_model
        fit_loss = loss_fit(licch, vidx, uid)
        _, gen_loss, _ = loss_s_gen_reg(licch, vidx)
        return fit_loss + gen_loss
    return get_loss


# FIXME take translation into account
def get_uncertainty_loc(licch):
    """ Returns uncertainty for all local scores

    Args:
        licch (Licchavi()): licchavi object

    Returns:
        (float tensor list): uncertainty for all local scores
    """
    logging.info('Computing uncertainty')
    local_uncert = []
    for uid, node in licch.nodes.items():  # for all nodes
        local_uncerts = []
        for vid in node.vids:  # for all videos of the node
            vidx = licch.vid_vidx[vid]  # video index
            score = node.model[vidx:vidx+1].detach()
            score = deepcopy(score)
            fun = _get_hessian_fun_loc(licch, uid, vidx)
            deriv2 = hessian(fun, score)
            uncert = deriv2**(-0.5)
            local_uncerts.append(uncert)
        local_uncert.append(local_uncerts)
    return local_uncert


# -------- to check equilibrium ------
def _random_signs(epsilon, nb_vids):
    """ Returns a tensor whith binary random coordinates

    epsilon (float): scores increment before computing gradient
    nb_vids (int): length of output tensor

    Returns:
        (float tensor): coordinates are +/-epsilon randomly
    """
    rand = torch.randint(2, size=(1, nb_vids))[0] - 0.5
    return rand * 2 * epsilon


def check_equilibrium_loc(epsilon, licch):
    """ Returns proportion of local scores which have converged

    Args:
        epsilon (float): precision of convergence required
        licch (Licchavi()): licchavi object

    Returns:
        ({int: float}): fraction of scores at equilibrium for each user ID
    """
    nbvid = len(licch.vid_vidx)
    incr = _random_signs(epsilon, nbvid)
    eq_fracs = {}

    def _one_node_eq(node, uid, increment):
        """ testing eq for one node """
        # resetting gradients
        node.opt.zero_grad(set_to_none=True)  # node optimizer
        # adding epsilon to scores
        with torch.no_grad():
            node.model += increment
        # computing gradients
        loss = loss_fit(licch, uid=uid)
        loss.backward()
        # restoring scores
        with torch.no_grad():
            node.model -= increment
        return node.model.grad * increment

    for uid, node in licch.nodes.items():
        derivs1 = _one_node_eq(node, uid, incr)
        derivs2 = _one_node_eq(node, uid, - incr)
        equilibrated = torch.logical_and(derivs1 > 0, derivs2 > 0)
        used = torch.logical_or(derivs1 != 0, derivs2 != 0)
        frac = torch.count_nonzero(equilibrated) / torch.count_nonzero(used)
        eq_fracs[uid] = frac.item()
    return eq_fracs


def check_equilibrium_glob(epsilon, licch):
    """ Returns proportion of global scores which have converged

    Args:
        licch (Licchavi()): licchavi object

    Returns:
        (float): fraction of scores at equilibrium
    """
    nbvid = len(licch.vid_vidx)
    incr = _random_signs(epsilon, nbvid)

    def _one_side_glob(increment):
        """ increment (float tensor): coordinates are +/- epsilon """
        licch.opt_gen.zero_grad(set_to_none=True)  # general optimizer

        # adding epsilon to scores
        with torch.no_grad():
            licch.global_model += increment
        _, gen_loss, reg_loss = loss_s_gen_reg(licch)
        loss = gen_loss + reg_loss
        loss.backward()
        derivs = licch.global_model.grad

        # removing epsilon from scores
        with torch.no_grad():
            licch.global_model -= increment
        return derivs * increment

    derivs1 = _one_side_glob(incr)
    derivs2 = _one_side_glob(-incr)
    equilibrated = torch.logical_and(derivs1 > 0, derivs2 > 0)
    frac_glob = torch.count_nonzero(equilibrated) / nbvid
    return frac_glob.item()
