import torch
import numpy as np

from .losses import round_loss

"""
Metrics used for training monitoring in "licchavi.py"

Main file "ml_train.py"
"""

# metrics on models
def extract_grad(model):
    ''' returns list of gradients of a model '''
    l_grad =  [p.grad for p in [model]]
    return l_grad

def sp(l_grad1, l_grad2):
    ''' scalar product of 2 lists of gradients '''
    s = 0
    for g1, g2 in zip(l_grad1, l_grad2):
        s += (g1 * g2).sum()
    return round_loss(s, 4)

def nb_params(model):
    ''' returns number of parameters of a model '''
    return sum(p.numel() for p in [model])
