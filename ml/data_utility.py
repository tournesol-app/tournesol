import torch
import numpy as np
import json
import pickle 

"""
Utility functions used in "handle_data.py"

Main file is "ml_train.py"
"""


# to handle data 
def rescale_rating(rating):
    ''' rescales from 0-100 to [-1,1] float '''
    return rating / 50 - 1

def get_all_vids(arr):
    ''' get all unique vIDs for one criteria (all users) '''
    return np.unique(arr[:,1:3])

def get_mask(batch1, batch2):
    ''' returns boolean tensor indicating which videos the user rated '''
    batch = batch1 + batch2
    to = batch.sum(axis=0, dtype=bool)
    return [to]

def sort_by_first(arr):
    ''' sorts 2D array lines by first element of lines '''
    order = np.argsort(arr,axis=0)[:,0]
    return arr[order,:]

def one_hot_vid(vid_vidx, vid):
    ''' One-hot inputs for neural network
    
    vid_vidx: dictionnary of {vID: idx}
    vid: vID

    Returns: 1D boolean tensor with 0s and 1 only for video index
    '''
    tens = torch.zeros(len(vid_vidx), dtype=bool)
    tens[vid_vidx[vid]] = True
    return tens

def one_hot_vids(vid_vidx, l_vid):
    ''' One-hot inputs for neural network, list to batch
    
    vid_vidx: dictionnary of {vID: idx}
    vid: list of vID

    Returns: 2D bollean tensor with one line being 0s and 1 only for video index
    '''
    batch = torch.zeros(len(l_vid), len(vid_vidx), dtype=bool)
    for idx, vid in enumerate(l_vid):
        batch[idx][vid_vidx[vid]] = True
    return batch

def reverse_idxs(vids):
    ''' Returns dictionnary of {vid: idx} '''
    vid_vidx = {}
    for idx, vid in enumerate(vids):
        vid_vidx[vid] = idx
    return vid_vidx 

# used for updating models after loading
def expand_tens(tens, nb_new):
    ''' Expands a tensor to include scores for new videos
    
    tens: a detached tensor 

    Returns:
    - expanded tensor requiring gradients
    '''
    full = torch.cat([tens, torch.zeros(nb_new)])
    full.requires_grad=True
    return full

def expand_dic(vid_vidx, l_vid_new):
    ''' Expands a dictionnary to include new videos IDs

    vid_vidx: dictionnary of {video ID: video idx}
    l_vid_new: int list of video ID
    
    Returns:
    - dictionnary of {video ID: video idx} updated (bigger)
    '''
    idx = len(vid_vidx)
    for vid_new in l_vid_new:
        if vid_new not in vid_vidx:
            vid_vidx[vid_new] = idx
            idx += 1
    return vid_vidx

# save and load data
def save_to_json(global_scores, local_scores, suff=""):
    ''' saves scores in json files '''
    with open("global_scores{}.json".format(suff), 'w') as f:
        json.dump(global_scores, f, indent=1) 
    with open("local_scores{}.json".format(suff), 'w') as f:
        json.dump(local_scores, f, indent=1) 

def load_from_json(suff=""):
    ''' loads previously saved data '''
    with open("global_scores{}.json".format(suff), 'r') as f:
        global_scores = json.load(f)
    with open("local_scores{}.json".format(suff), 'r') as f:
        local_scores = json.load(f)
    return global_scores, local_scores

def save_to_pickle(obj, name="pickle"):
    ''' save python object to pickle file '''
    filename = '{}.p'.format(name)
    with open(filename, 'wb') as filehandler:
        pickle.dump(obj, filehandler)

def load_from_pickle(name="pickle"):
    filename = '{}.p'.format(name)
    with open(filename, 'rb') as filehandler:
        obj = pickle.load(filehandler)
    return obj
