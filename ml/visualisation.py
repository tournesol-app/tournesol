import numpy as np
import torch

"""
Visualisation methods, mainly for testing and debugging

Main file is "ml_train.py"
"""


# debug helpers
def check_one(vid, comp_glob, comp_loc):
    ''' prints global and local scores for one video '''
    print("all we have on video: ", vid)
    for score in comp_glob:
        if score[0]==vid:
            print(score)
    for score in comp_loc:
        if score[1]==vid:
            print(score)

def seedall(s):
    ''' seeds all sources of randomness '''
    reproducible = (s >= 0)
    torch.manual_seed(s)
    #random.seed(s)
    np.random.seed(s)
    torch.backends.cudnn.deterministic = reproducible
    torch.backends.cudnn.benchmark     = not reproducible
    print("\nSeeded all to", s)

def disp_one_by_line(it):
    ''' prints one iteration by line '''
    for obj in it:
        print(obj)
