"""
Node class used in "licchavi.py"
"""

import torch


class Node:
    def __init__(
            self, vid1, vid2, rating, vids,
            mask, t_par, s_par, model,
            lr_loc, lr_t, lr_s, opt):
        """
        vid1 (bool 2D tensor): one line is a one-hot-encoded video index
        vid2 (bool 2D tensor): one line is a one-hot-encoded video index
        rating (float tensor): comparisons corresponding to vid1 and vid2 lines
        vids (int array): IDs of all videos rated at least once by user
        mask (bool tensor): True for all video indexes rated by user
        t_par (float tensor): t (translation) learnable parameter
        s_par (float tensor): s (scaling) learnable parameter
        model (float tensor): learnable tensor of all video scores
        lr_loc (float): learning rate of self.model
        lr_t (float): learning rate of self.t_par
        lr_s (float): learning rate of self.s_par
        opt (torch.optim.Optimizer): gradient descent optimizer
        """
        self.vid1 = vid1
        self.vid2 = vid2
        self.rating = rating
        self.vids = vids
        self.mask = mask
        self.t_par = t_par
        self.s_par = s_par
        self.model = model
        self.lr_t = lr_t / len(vids)  # adaptative lr
        self.lr_s = lr_s / len(vids)  # adaptative lr
        self.opt = opt(
            [
                {'params': self.model},
            ],
            lr=lr_loc
        )
        self.opt_t_s = opt(
            [
                {'params': self.t_par, 'lr': self.lr_t},
                {'params': self.s_par, 'lr': self.lr_s},
            ]
        )
        self.nb_comps = self._count_comps()  # number of comps of each video
        self.delta_na = 1 / torch.sqrt(self.nb_comps)  # needed for loss later
        _ = torch.nan_to_num_(self.delta_na, posinf=1)  # avoiding NaNs
        nb_loc_vids = torch.sum(mask.int())  # nb of videos rated by user
        factor = nb_loc_vids / (300 + nb_loc_vids)
        self.w_na = self.nb_comps / (5 + self.nb_comps) * factor

    def _count_comps(self):
        """ Counts number of comparisons for each video

        Returns:
            (int tensor): number of comparisons for each video index
        """
        return torch.sum(self.vid1, axis=0) + torch.sum(self.vid2, axis=0)
