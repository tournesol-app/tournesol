import torch

"""
Node class used in "licchavi.py"

Main file is "ml_train.py"
"""


class Node:
    def __init__(self, vid1, vid2, r, vids,
                 mask, s, model, age, w, lr_node, lr_s, opt):
        """
        vid1 (bool 2D tensor): one line is a one-hot-encoded video index
        vid2 (bool 2D tensor): one line is a one-hot-encoded video index
        r (float tensor): comparisons corresponding to vid1 and vid2 lines
        mask (bool tensor): True for all video indexes rated by user
        s (float tensor): s scaling learnable parameter
        model (float tensor): learnable tensor of all video scores
        age (int): number of epochs this node has been trained
        w (float): node ponderation for generalisation (its influence)
        lr_node (float): learning rate of self.model
        lr_s (float): learning rate of self.s
        opt (torch.optim.Optimizer): gradient descent optimizer
        """
        self.vid1 = vid1
        self.vid2 = vid2
        self.r = r
        self.vids = vids
        self.mask = mask
        self.s = s
        self.model = model
        self.age = age  # number of epochs the node has been trained
        self.w = w

        self.lr_s = lr_s / len(vid1)
        self.opt = opt(
            [
                {'params': self.model},
                {'params': self.s, 'lr': self.lr_s},
            ],
            lr=lr_node
        )

        self.nb_comps = self._count_comps()
        self.delta_na = 1 / torch.sqrt(self.nb_comps)
        for i, val in enumerate(self.delta_na):
            if torch.isinf(val):
                self.delta_na[i] = 1

    def _count_comps(self):
        """ Counts number of comparisons for each video

        Returns:
            (int tensor): number of comparison for each video index
        """
        return torch.sum(self.vid1, axis=0) + torch.sum(self.vid2, axis=0)
