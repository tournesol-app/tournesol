"""
Node class used in "licchavi.py"
"""

import torch


class Node:
    def __init__(self, vid1, vid2, rating, vids,
                 mask, s_param, model, age, weight, lr_loc, lr_s, opt):
        """
        vid1 (bool 2D tensor): one line is a one-hot-encoded video index
        vid2 (bool 2D tensor): one line is a one-hot-encoded video index
        rating (float tensor): comparisons corresponding to vid1 and vid2 lines
        mask (bool tensor): True for all video indexes rated by user
        s_param (float tensor): s scaling learnable parameter
        model (float tensor): learnable tensor of all video scores
        age (int): number of epochs this node has been trained
        weight (float): node ponderation for generalisation (its influence)
        lr_loc (float): learning rate of self.model
        lr_s (float): learning rate of self.s
        opt (torch.optim.Optimizer): gradient descent optimizer
        """
        self.vid1 = vid1
        self.vid2 = vid2
        self.rating = rating
        self.vids = vids
        self.mask = mask
        self.s_param = s_param
        self.model = model
        self.age = age
        self.weight = weight
        self.lr_s = lr_s / len(vid1)
        self.opt = opt(
            [
                {'params': self.model},
                {'params': self.s_param, 'lr': self.lr_s},
            ],
            lr=lr_loc
        )

        self.nb_comps = self._count_comps()  # number of comparisons
        self.delta_na = 1 / torch.sqrt(self.nb_comps)  # needed for loss later
        _ = torch.nan_to_num_(self.delta_na, posinf=1)  # avoiding NaNs

    def _count_comps(self):
        """ Counts number of comparisons for each video

        Returns:
            (int tensor): number of comparison for each video index
        """
        return torch.sum(self.vid1, axis=0) + torch.sum(self.vid2, axis=0)
