import numpy as np
import torch

from .data_utility import rescale_rating, sort_by_first, one_hot_vids
from .data_utility import reverse_idxs, get_mask, get_all_vids, expand_dic

"""
To prepare data from training and reshape it after training

Main file is "ml_train.py"
"""


def select_criteria(comparison_data, crit):
    ''' Extracts not None comparisons of one criteria

    comparison_data: output of fetch_data()
    crit: str, name of criteria
        
    Returns: 
    - list of all ratings for this criteria
        ie list of [contributor_id: int, video_id_1: int, video_id_2: int, 
                    criteria: str (crit), score: float, weight: float]  
    '''
    l_ratings = [comp for comp 
                        in comparison_data 
                        if (comp[3] == crit and comp[4] is not None)]
    return l_ratings

def shape_data(l_ratings):
    ''' Shapes data for distribute_data()/distribute_data_from_save()

    l_ratings : list of not None ratings for one criteria, all users

    Returns : one array with 4 columns : userID, vID1, vID2, rating ([-1,1]) 
    '''
    l_clear = [rating[:3] + [rescale_rating(rating[4])] for rating in l_ratings]
    arr = np.asarray(l_clear)
    return arr

def distribute_data(arr, gpu=False): # change to add user ID to tuple
    ''' Distributes data on nodes according to user IDs for one criteria
        Output is not compatible with previously stored models, 
           ie starts from scratch

    arr: np 2D array of all ratings for all users for one criteria
            (one line is [userID, vID1, vID2, score])

    Returns:
    - dictionnary {userID: (vID1_batch, vID2_batch, 
                            rating_batch, single_vIDs, mask)}
    - array of user IDs
    - dictionnary of {vID: video idx}
    '''
    arr = sort_by_first(arr) # sorting by user IDs
    user_ids, first_of_each = np.unique(arr[:,0], return_index=True)
    first_of_each = list(first_of_each) # to be able to append
    first_of_each.append(len(arr)) # to have last index too
    vids = get_all_vids(arr)  # all unique video IDs
    vid_vidx = reverse_idxs(vids) # dictionnary of  {vID: video idx}
    nodes_dic = {}   # futur dictionnary of data for each user

    for i, id in enumerate(user_ids):
        node_arr = arr[first_of_each[i]: first_of_each[i+1], :]
        vid1 = node_arr[:,1] # iterable of video IDs
        vid2 = node_arr[:,2]
        batchvids = get_all_vids(node_arr) # unique video IDs of node
        batch1 = one_hot_vids(vid_vidx, vid1)
        batch2 = one_hot_vids(vid_vidx, vid2)
        mask = get_mask(batch1, batch2) # which videos are rated by user
        batchout = torch.FloatTensor(node_arr[:,3])
        nodes_dic[id] = (batch1, batch2, batchout, batchvids, mask)
    return nodes_dic, user_ids, vid_vidx

def distribute_data_from_save(arr, crit, fullpath, gpu=False):
    ''' Distributes data on nodes according to user IDs for one criteria
        Output is compatible with previously stored models

    arr: np 2D array of all ratings for all users for one criteria
            (one line is [userID, vID1, vID2, score])

    Returns:
    - dictionnary {userID: (vID1_batch, vID2_batch, 
                            rating_batch, single_vIDs, masks)}
    - array of user IDs
    - dictionnary of {vID: video idx}
    '''
    _, dic_old, _, _ = torch.load(fullpath) # loading previous data

    arr = sort_by_first(arr) # sorting by user IDs
    user_ids, first_of_each = np.unique(arr[:,0], return_index=True)
    first_of_each = list(first_of_each) # to be able to append
    first_of_each.append(len(arr)) # to have last index too
    vids = get_all_vids(arr)  # all unique video IDs
    vid_vidx = expand_dic(dic_old, vids) # update dictionnary
    nodes_dic = {}    # futur list of data for each user

    for i, id in enumerate(user_ids):
        node_arr = arr[first_of_each[i]: first_of_each[i+1], :]
        vid1 = node_arr[:,1] # iterable of video IDs
        vid2 = node_arr[:,2]
        batchvids = get_all_vids(node_arr) # unique video IDs of node
        batch1 = one_hot_vids(vid_vidx, vid1)
        batch2 = one_hot_vids(vid_vidx, vid2)
        mask = get_mask(batch1, batch2) # which videos are rated by user
        batchout = torch.FloatTensor(node_arr[:,3])
        nodes_dic[id] = (batch1, batch2, batchout, batchvids, mask)
    return nodes_dic, user_ids, vid_vidx

def format_out_glob(glob, crit):
    ''' Puts data in list of global scores (one criteria)
    
    glob: (tensor of all vIDS , tensor of global video scores)
    crit: criteria
    
    Returns: 
    - list of [video_id: int, criteria_name: str, 
                score: float, uncertainty: float]
    '''
    l_out = []
    ids, scores = glob
    for i in range(len(ids)):
         # uncertainty is 0 for now
        out = [int(ids[i]), crit, round(scores[i].item(), 2), 0]
        l_out.append(out)
    return l_out

def format_out_loc(loc, users_ids, crit):
    ''' Puts data in list of local scores (one criteria)

    loc: (list of tensor of local vIDs , list of tensors of local video scores)
    users_ids: list/array of user IDs in same order
    
    Returns : 
    - list of [contributor_id: int, video_id: int, criteria_name: str, 
                score: float, uncertainty: float]
    '''
    l_out = []
    vids, scores = loc
    for user_id, user_vids, user_scores in zip(users_ids, vids, scores):
        for i in range(len(user_vids)):
            # uncertainty is 0 for now
            out = [int(user_id), int(user_vids[i].item()), 
                    crit, round(user_scores[i].item(), 2), 0] 
            l_out.append(out)
    return l_out
    