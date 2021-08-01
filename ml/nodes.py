"""
Node class used in "licchavi.py"

Main file is "ml_train.py"
"""


class Node:
    def __init__(self, vid1, vid2, r, vids,
                 mask, s, model, age, w, lr_node, lr_s, opt):
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
