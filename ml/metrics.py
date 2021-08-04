from torch.autograd.functional import hessian
import torch
from copy import deepcopy
import logging
from statistics import median

from .losses import round_loss, loss_fit_s_gen, loss_gen_reg, models_dist

"""
Metrics used for training monitoring in "licchavi.py"

Main file "ml_train.py"
"""


# metrics on models
def extract_grad(model):
    """returns list of gradients of a model

    model (float tensor): torch tensor with gradients

    Returns:
        (float tensor list): list of gradients of the model
    """
    return [p.grad for p in [model]]


def scalar_product(l_grad1, l_grad2):
    """scalar product of 2 lists of gradients

    l_grad1 (float tensor list): list of gradients of a model
    l_grad2 (float tensor list): list of gradients of a model

    Returns:
        (float): scalar product of the gradients
    """
    s = 0
    for g1, g2 in zip(l_grad1, l_grad2):
        s += (g1 * g2).sum()
    return round_loss(s, 4)


def replace_coordinate(tens, score, idx):
    """Replaces one coordinate of the tensor

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


# ------ to compute uncertainty -------
def _global_uncert(values, prior=4, weight=5):
    """Returns posterior value of median

    prior(float): value of prior median
    weight (int): weight of prior
    values (float list): data to take median of

    Returns:
        (float): global uncertainty for one video
    """
    full_values = values + [prior] * weight
    return median(full_values) / len(values) ** 0.5


def get_uncertainty_glob(licch):
    """Returns uncertainty for all global scores

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
                    dist = models_dist(node.model, licch.global_model, vidx=vidx)
                    distances.append(dist.item())
            uncerts[vidx] = _global_uncert(distances)
    return uncerts


def _get_hessian_fun_loc(licch, uid, vidx):
    """Gives loss in function of local model for hessian computation

    Args:
        licch (Licchavi()): licchavi object
        id_node (int): id of user
        vidx (int): index of video, ie index of parameter

    Returns:
        (scalar tensor -> float) function giving loss according to one score
    """

    def get_loss(score):
        """Used to compute its second derivative to get uncertainty

        input (float scalar tensor): one score

        Returns:
            (float scalar tensor): partial loss for 1 user, 1 video
        """
        new_model = replace_coordinate(licch.nodes[uid].model, score, vidx)
        licch.nodes[uid].model = new_model
        fit_loss, _, gen_loss = loss_fit_s_gen(licch, vidx, uid)
        return fit_loss + gen_loss

    return get_loss


def get_uncertainty_loc(licch):
    """Returns uncertainty for all local scores

    Args:
        licch (Licchavi()): licchavi object

    Returns:
        (float tensor list): uncertainty for all local scores
    """
    logging.info("Computing uncertainty")
    local_uncert = []
    for uid, node in licch.nodes.items():  # for all nodes
        local_uncerts = []
        for vid in node.vids:  # for all videos of the node
            vidx = licch.vid_vidx[vid]  # video index
            score = node.model[vidx : vidx + 1].detach()
            score = deepcopy(score)
            fun = _get_hessian_fun_loc(licch, uid, vidx)
            deriv2 = hessian(fun, score)
            uncert = deriv2 ** (-0.5)
            local_uncerts.append(uncert)
        local_uncert.append(local_uncerts)
    return local_uncert


# -------- to check equilibrium ------
def _random_signs(epsilon, nb_vids):
    """Returns a tensor whith binary random coordinates

    epsilon (float): scores increment before computing gradient
    nb_vids (int): length of output tensor

    Returns:
        (float tensor): coordinates are +/-epsilon randomly
    """
    rand = torch.randint(2, size=(1, nb_vids))[0] - 0.5
    return rand * 2 * epsilon


def check_equilibrium_glob(epsilon, licch):
    """Returns proportion of global scores which have converged

    Args:
        licch (Licchavi()): licchavi object

    Returns:
        (float): fraction of scores at equilibrium
    """
    nbvid = len(licch.vid_vidx)
    incr = _random_signs(epsilon, nbvid)

    def _one_side_glob(increment):
        """increment (float tensor): coordinates are +/- epsilon"""
        for node in licch.nodes.values():
            node.opt.zero_grad(set_to_none=True)  # node optimizer
        licch.opt_gen.zero_grad(set_to_none=True)  # general optimizer

        # adding epsilon to scores
        with torch.no_grad():
            licch.global_model += increment
        gen_loss, reg_loss = loss_gen_reg(licch)
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


def check_equilibrium_loc(epsilon, licch):
    """Returns proportion of local scores which have converged

    Args:
        licch (Licchavi()): licchavi object

    Returns:
        (float): fraction of scores at equilibrium
    """
    nbvid = len(licch.vid_vidx)
    nbn = len(licch.nodes)
    incr = _random_signs(epsilon, nbvid)

    def _one_side_loc(increment):
        """increment (float tensor): coordinates are +/- epsilon"""
        l_derivs = torch.empty(nbn, nbvid)
        # resetting gradients
        for node in licch.nodes.values():
            node.opt.zero_grad(set_to_none=True)  # node optimizer
        licch.opt_gen.zero_grad(set_to_none=True)  # general optimizer
        # adding epsilon to scores
        with torch.no_grad():
            for node in licch.nodes.values():
                node.model += increment
        # computing gradients
        fit_loss, _, gen_loss = loss_fit_s_gen(licch)
        loss = fit_loss + gen_loss
        loss.backward()
        # adding derivatives
        for uidx, node in enumerate(licch.nodes.values()):
            l_derivs[uidx] = node.model.grad * increment
        # removing epsilon from score
        with torch.no_grad():
            for node in licch.nodes.values():
                node.model -= increment
        return l_derivs

    derivs1 = _one_side_loc(incr)
    derivs2 = _one_side_loc(-incr)
    equilibrated = torch.logical_and(derivs1 > 0, derivs2 > 0)
    used = torch.logical_or(derivs1 != 0, derivs2 != 0)
    frac_loc = torch.count_nonzero(equilibrated) / torch.count_nonzero(used)
    return frac_loc.item()
