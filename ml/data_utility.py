import torch
import numpy as np
import json
import pickle

"""
Utility functions used in "handle_data.py"

Main file is "ml_train.py"
"""


def rescale_rating(rating):
    """rescales from [0,100] to [-1,1] float"""
    return rating / 50 - 1


def get_all_vids(arr):
    """get all unique vIDs for one criteria (all users)

    arr (2D float array): 1 line is [userID, vID1, vID2, r]

    Returns:
        (float array): unique video IDs
    """
    return np.unique(arr[:, 1:3])  # columns 1 and 2 are what we want


def get_mask(batch1, batch2):
    """returns boolean tensor indicating which videos the user rated

    batch1 (2D bool tensor): 1 line is a one-hot encoded video index
    batch2 (2D bool tensor): 1 line is a one-hot encoded video index

    Returns:
        (bool tensor): True for all indexes rated by the user
    """
    return torch.sum(batch1 + batch2, axis=0, dtype=bool)


def sort_by_first(arr):
    """sorts 2D array lines by first element of lines"""
    order = np.argsort(arr, axis=0)[:, 0]
    return arr[order, :]


def one_hot_vid(vid_vidx, vid):
    """One-hot inputs for neural network

    vid_vidx (dictionnary): dictionnary of {vID: idx}
    vid (int): video ID

    Returns:
        (1D boolean tensor): one-hot encoded video index
    """
    tens = torch.zeros(len(vid_vidx), dtype=bool)
    tens[vid_vidx[vid]] = True
    return tens


def one_hot_vids(vid_vidx, l_vid, device="cpu"):
    """One-hot inputs for neural network, list to batch

    vid_vidx (int dictionnary): dictionnary of {vID: vidx}
    vid (int list): list of vID
    device (str): device used (cpu/gpu)

    Returns:
        (2D boolean tensor): one line is one-hot encoded video index
    """
    batch = torch.zeros(len(l_vid), len(vid_vidx), dtype=bool, device=device)
    for idx, vid in enumerate(l_vid):
        batch[idx][vid_vidx[vid]] = True
    return batch


def get_batch_r(node_arr, device="cpu"):
    """Returns batch of one user's ratings

    node_arr (2D float array): one line is [userID, vID1, vID2, rating]
    device (str): device used (cpu/gpu)

    Returns:
        (float tensor): batch of ratings
    """
    return torch.FloatTensor(node_arr[:, 3], device=device)


def reverse_idxs(vids):
    """Returns dictionnary of {vid: vidx}

    vids (int iterable): unique video IDs

    Returns:
        (int:int dictionnary): dictionnary of {videoID: video index}
    """
    return {vid: idx for idx, vid in enumerate(vids)}


# used for updating models after loading
def expand_tens(tens, nb_new, device="cpu"):
    """Expands a tensor to include scores for new videos

    tens (tensor): a detached tensor
    nb_new (int): number of parameters to add
    device (str): device used (cpu/gpu)

    Returns:
        (tensor): expanded tensor requiring gradients
    """
    expanded = torch.cat([tens, torch.zeros(nb_new, device=device)])
    expanded.requires_grad = True
    return expanded


def expand_dic(vid_vidx, l_vid_new):
    """Expands a dictionnary to include new videos IDs

    vid_vidx: dictionnary of {video ID: video idx}
    l_vid_new: int list of video ID

    Returns:
    - dictionnary of {video ID: video idx} updated (bigger)
    """
    idx = len(vid_vidx)
    for vid_new in l_vid_new:
        if vid_new not in vid_vidx:
            vid_vidx[vid_new] = idx
            idx += 1
    return vid_vidx


# save and load data
def save_to_json(global_scores, local_scores, suff=""):
    """saves scores in json files"""
    with open("global_scores{}.json".format(suff), "w") as f:
        json.dump(global_scores, f, indent=1)
    with open("local_scores{}.json".format(suff), "w") as f:
        json.dump(local_scores, f, indent=1)


def load_from_json(suff=""):
    """loads previously saved data"""
    with open("global_scores{}.json".format(suff), "r") as f:
        global_scores = json.load(f)
    with open("local_scores{}.json".format(suff), "r") as f:
        local_scores = json.load(f)
    return global_scores, local_scores


def save_to_pickle(obj, name="pickle"):
    """save python object to pickle file"""
    filename = "{}.p".format(name)
    with open(filename, "wb") as filehandler:
        pickle.dump(obj, filehandler)


def load_from_pickle(name="pickle"):
    """load python object from pickle file"""
    filename = "{}.p".format(name)
    with open(filename, "rb") as filehandler:
        obj = pickle.load(filehandler)
    return obj
