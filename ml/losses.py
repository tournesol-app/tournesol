"""
Losses used in "licchavi.py"
"""

import torch


def predict(input, tens, mask=None):
    """ Predicts score according to a model

    Args:
        input (bool 2D tensor): one line is a one-hot encoded video index
        tens (float tensor): tensor = model
        mask (bool tensor): one element is bool for using this comparison

    Returns:
        (2D float tensor): score of the videos according to the model
    """
    if input.shape[1] == 0:  # if empty input
        return torch.zeros((1, 1))
    if mask is not None:
        return torch.where(
            mask,
            torch.matmul(input.float(), tens),
            torch.zeros(1)
        )
    return torch.matmul(input.float(), tens)


# losses (used in licchavi.py)
def _bbt_loss(t, r):
    """ Binomial Bradley-Terry loss function (used for test only)

    Used only for testing

    Args:
        t (float tensor): batch of (ya - yb)
        r (float tensor): batch of ratings given by user.

    Returns:
        (float tensor): sum of empirical losses for all comparisons of one user
    """
    two = torch.tensor(2)
    losses = torch.log(torch.sinh(t)/t) + r * t + torch.log(two)
    return sum(losses)


@torch.jit.script  # to optimize computation time
def _approx_bbt_loss(t, r):
    """ Approximated Binomial Bradley-Terry loss function (used in Licchavi)

    Args:
        t (float tensor): batch of (ya - yb)
        r (float tensor): batch of ratings given by user.

    Returns:
        (float tensor): sum of empirical losses for all comparisons of one user
    """

    small = abs(t) <= 0.01
    medium = torch.logical_and((abs(t) < 10), (abs(t) > 0.01))
    big = abs(t) >= 10
    zer = torch.zeros(1)
    loss = 0

    loss += torch.where(
        small,
        t**2 / 6 + r * t + torch.log(torch.tensor(2)),
        zer
    ).sum()
    tt = torch.where(t != 0, t, torch.ones(1))  # trick to avoid zeros so NaNs
    loss += torch.where(
        medium,
        torch.log(2 * torch.sinh(tt) / tt) + r * tt,
        zer
    ).sum()
    loss += torch.where(big, abs(tt) - torch.log(abs(tt)) + r * tt, zer).sum()

    return loss


def get_fit_loss(model, s, a_batch, b_batch, r_batch, vidx=-1):
    """ Fitting loss for one node

    Args:
        model (float tensor): node local model.
        s (float tensor): s parameter.
        a_batch (bool 2D tensor): first videos compared by user.
        b_batch (bool 2D tensor): second videos compared by user.
        r_batch (float tensor): rating provided by user.

    Returns:
        (float scalar tensor): fitting loss.
    """
    if vidx != -1:  # loss for only one video (for uncertainty computation)

        idxs = torch.tensor(
            [idx for idx, ab in enumerate(zip(a_batch, b_batch))
                if (ab[0][vidx] or ab[1][vidx])],
            dtype=torch.long
        )

        if idxs.shape[0] == 0:  # if user didnt rate video
            return torch.scalar_tensor(0)

        ya_batch = predict(a_batch[idxs], model)
        yb_batch = predict(b_batch[idxs], model)
        loss = _approx_bbt_loss(ya_batch - yb_batch, r_batch[idxs])
    else:
        ya_batch = predict(a_batch, model)
        yb_batch = predict(b_batch, model)
        loss = _approx_bbt_loss(ya_batch - yb_batch, r_batch)
    return loss


def get_s_loss(s):
    """ Scaling loss for one node

    Args:
        s (float tensor): s parameter.

    Returns:
        float tensor: second half of local loss
    """
    return 0.5 * s**2 - torch.log(s)


def models_dist(model1, model2, pow=(1, 1), mask=None, vidx=-1):
    """ distance between 2 models (l1 by default)

    Args:
        model1 (float tensor): scoring model
        model2 (float tensor): scoring model
        pow (float, float): (internal power, external power)
        mask (bool tensor): subspace in which to compute distance
        vidx (int): video index if only one is computed (-1 for all)

    Returns:
        (scalar float tensor): distance between the 2 models
    """
    q, p = pow
    if vidx == -1:  # if we want several coordinates
        if mask is None:  # if we want all coordinates
            dist = ((model1 - model2)**q).abs().sum()**p
        else:
            dist = (((model1 - model2) * mask)**q).abs().sum()**p
    else:  # if we want only one coordinate
        dist = abs(model1[vidx] - model2[vidx])**(q*p)
    return dist


def _huber(x, d):
    """ Pseudo-Huber loss function

    x (float tensor): input
    d (float tensor): parameters (d → 0 for absolute value)

    Returns:
        (float): Huber loss
    """
    return d * (torch.sqrt(1 + (x/d)**2) - 1)


def models_dist_huber(model1, model2, mask=None, s=1, vidx=-1, d=1):
    """ Pseudo-Huber distance between 2 models

    Args:
        model1 (float tensor): scoring model
        model2 (float tensor): scoring model
        mask (bool tensor): subspace in which to compute distance
        vidx (int): video index if only one is computed (-1 for all)
        d (float tensor): pseudo-Huber loss parameters
                            (d → 0 for absolute value)
                            (defined in hyperparameters.gin)

    Returns:
        (scalar float tensor): distance between the 2 models
    """
    if vidx == -1:  # if we want several coordinates
        if mask is None:  # if we want all coordinates
            dist = (_huber(s * (model1 - model2), d)).sum()
        else:
            dist = (_huber(s * (model1 - model2) * mask, d)).sum()
    else:  # if we want only one coordinate
        dist = _huber(s * (model1[vidx] - model2[vidx]), d[vidx])
    return dist


def model_norm(model, pow=(2, 1), vidx=-1):
    """ norm of a model (l2 squared by default)

    Args:
        model (float tensor): scoring model
        pow (float, float): (internal power, external power)
        vidx (int): video index if only one is computed (-1 for all)

    Returns:
        (float scalar tensor): norm of the model
    """
    q, p = pow
    if vidx != -1:  # if we use only one video
        return abs(model[vidx])**(q*p)
    return (model**q).abs().sum()**p


# losses used in "licchavi.py"
def loss_fit_s_gen(licch, vidx=-1, uid=-1):  # FIXME shorten
    """ Computes local and generalisation terms of loss

    Args:
        licch (Licchavi()): licchavi object
        vidx (int): video index if we are interested in partial loss
                                    (-1 for all indexes)
        uid (int): user ID if we are interested in partial loss
                                    (-1 for all users)

    Returns:
        (float tensor): sum of local terms of loss
        (float tensor): generalisation term of loss
    """

    fit_loss, s_loss, gen_loss = 0, 0, 0

    def _one_node_loss(fit_loss, s_loss, gen_loss, node, vidx=-1):
        fit_loss += get_fit_loss(
            node.model,
            node.s,
            node.vid1,  # idx1_batch
            node.vid2,  # idx2_batch
            node.r,     # r_batch
            vidx=vidx   # video index if we want partial loss
        )
        if vidx == -1:  # only if all loss is computed
            s_loss += licch.nu * get_s_loss(node.s)

        g = models_dist_huber(
            node.model,
            licch.global_model,
            mask=node.mask,
            s=node.s,
            vidx=vidx,     # video index if we want partial loss
            d=node.delta_na
        )
        gen_loss += node.w * g  # node weight  * generalisation term

        return fit_loss, s_loss, gen_loss

    if uid != -1:  # if we want only one user
        node = licch.nodes[uid]
        fit_loss, s_loss, gen_loss = _one_node_loss(
            fit_loss, s_loss, gen_loss, node, vidx=vidx
        )
    else:  # if we want all users
        for node in licch.nodes.values():
            fit_loss, s_loss, gen_loss = _one_node_loss(
                fit_loss, s_loss, gen_loss, node, vidx=vidx
            )
    return fit_loss, s_loss, gen_loss


def loss_gen_reg(licch, vidx=-1):
    """ Computes generalisation and regularisation terms of loss

    Args:
        licch (Licchavi()): licchavi object
        vidx (int): video index if we are interested in partial loss
                            (-1 for all indexes)

    Returns:
        (float tensor): generalisation term of loss
        (float tensor): regularisation loss (of general model)
    """
    gen_loss, reg_loss = 0, 0
    for node in licch.nodes.values():
        g = models_dist_huber(
            node.model,    # local model
            licch.global_model,  # general model
            mask=node.mask,     # mask
            s=node.s,
            vidx=vidx,
            d=node.delta_na
        )
        gen_loss += node.w * g  # node weight * generalisation term
    reg_loss = licch.w0 * model_norm(licch.global_model, vidx=vidx)
    return gen_loss, reg_loss


def round_loss(tens, dec=0):
    """ from an input scalar tensor or int/float returns rounded int/float """
    if isinstance(tens, (int, float)):
        return round(tens, dec)
    return round(tens.item(), dec)
