import logging
from typing import Iterable, Tuple

import numpy as np
import torch
from ml.losses import round_loss

from .data_utility import (
    expand_dic,
    get_all_vids,
    get_batch_r,
    get_mask,
    one_hot_vids,
    rescale_rating,
    reverse_idxs,
    sort_by_first,
)

"""
To prepare data from training and reshape it after training

Main file is "ml_train.py"
"""


def select_criteria(comparison_data: Iterable[Tuple[int, int, int, str, float, float]],
                    criteria_name: str):
    """Extracts not None comparisons of one criteria

    comparison_data: output of fetch_data(), can be an iterable of tuple of size 6
    criteria_name: str

    Returns:
    - list of all ratings for this criteria
        ie list of [contributor_id: int, video_id_1: int, video_id_2: int,
                    criteria: str (crit), score: float, weight: float]
    """
    # TODO Check if l_ratings is used as a list, not as an iterable or sequence.
    l_ratings = [
        comparison for comparison in comparison_data
        if comparison[3] == criteria_name and comparison[4] is not None
    ]
    return l_ratings


def shape_data(l_ratings):
    """Shapes data for distribute_data()/distribute_data_from_save()

    l_ratings : list of not None ratings ([0,100]) for one criteria, all users

    Returns : one array with 4 columns : userID, vID1, vID2, rating ([-1,1])
    """
    l_clear = [rating[:3] + [rescale_rating(rating[4])] for rating in l_ratings]
    return np.asarray(l_clear)


def _distribute_data_handler(arr, user_ids, vid_vidx, first_of_each, device="cpu"):
    """Utility for data distribution accross nodes

    arr (2D array): all ratings for all users for one criteria
                    (one line is [userID, vID1, vID2, rating])
    users_ids (array): users IDs
    vid_vidx (dict): {video ID: video index}
    first_of_each (int list): index of first comparison of each user in -arr
    device (str): device to use (cpu/gpu)

    Returns:
        (dict): {user ID : tuple of user's data}
    """
    nodes_dic = {}

    for i, id in enumerate(user_ids):
        node_arr = arr[first_of_each[i]: first_of_each[i + 1], :]

        batch1 = one_hot_vids(vid_vidx, node_arr[:, 1], device)
        batch2 = one_hot_vids(vid_vidx, node_arr[:, 2], device)

        nodes_dic[id] = (
            batch1,
            batch2,
            get_batch_r(node_arr, device),
            get_all_vids(node_arr),
            get_mask(batch1, batch2),
        )

    return nodes_dic


def distribute_data(arr, device="cpu"):
    """Distributes data on nodes according to user IDs for one criteria
        Output is not compatible with previously stored models,
           ie starts from scratch

    arr (2D array): all ratings for all users for one criteria
                        (one line is [userID, vID1, vID2, rating])
    device (str): device to use (cpu/gpu)


    Returns:
    - dictionnary {userID: (vID1_batch, vID2_batch,
                            rating_batch, single_vIDs, mask)}
    - array of user IDs
    - dictionnary of {vID: video idx}
    """
    logging.info("Preparing data from scratch")
    arr = sort_by_first(arr)  # sorting by user IDs
    user_ids, first_of_each = np.unique(arr[:, 0], return_index=True)
    first_of_each = list(first_of_each)  # to be able to append
    first_of_each.append(len(arr))  # to have last index too
    vid_vidx = reverse_idxs(get_all_vids(arr))

    nodes_dic = _distribute_data_handler(
        arr, user_ids, vid_vidx, first_of_each, device=device
    )

    return nodes_dic, user_ids, vid_vidx


def distribute_data_from_save(arr, fullpath, device):
    """Distributes data on nodes according to user IDs for one criteria
        Output is compatible with previously stored models

    arr: np 2D array of all ratings for all users for one criteria
            (one line is [userID, vID1, vID2, score])
    fullpath (str): path of saved previous training state
    device (str): device to use (cpu/gpu)

    Returns:
    - dictionnary {userID: (vID1_batch, vID2_batch,
                            rating_batch, single_vIDs, masks)}
    - array of user IDs
    - dictionnary of {vID: video idx}
    """
    logging.info("Preparing data from save")
    _, dic_old, _, _ = torch.load(fullpath)  # loading previous data

    arr = sort_by_first(arr)  # sorting by user IDs
    user_ids, first_of_each = np.unique(arr[:, 0], return_index=True)
    first_of_each = list(first_of_each)  # to be able to append
    first_of_each.append(len(arr))  # to have last index too
    vids = get_all_vids(arr)  # all unique video IDs
    vid_vidx = expand_dic(dic_old, vids)  # update dictionnary

    nodes_dic = _distribute_data_handler(
        arr, user_ids, vid_vidx, first_of_each, device=device
    )

    return nodes_dic, user_ids, vid_vidx


def format_out_glob(glob, crit, uncerts):
    """Puts data in list of global scores (one criteria)

    glob: (tensor of all vIDS , tensor of global video scores)
    crit (str): criteria
    uncerts (float list): uncertainty of global scores


    Returns:
    - list of [video_id: int, criteria_name: str,
                score: float, uncertainty: float]
    """
    return [
        [
            int(vid),
            crit,
            round_loss(score, 2),
            0 if uncerts is None else round_loss(uncerts[vidx], 2),
        ]
        for vid, score, vidx in zip(*glob, range(len(glob[0])))
    ]


def format_out_loc(loc, users_ids, crit, uncerts):
    """Puts data in list of local scores (one criteria)

    loc: (list of tensor of local vIDs , list of tensors of local video scores)
    users_ids: list/array of user IDs in same order
    crit (str): criteria
    uncerts (float list list): uncertainty of local scores

    Returns :
    - list of [contributor_id: int, video_id: int, criteria_name: str,
                score: float, uncertainty: float]
    """
    l_out = []
    vids, scores = loc
    for user_id, user_vids, user_scores, uidx in zip(
        users_ids, vids, scores, range(len(loc[0]))
    ):
        for i in range(len(user_vids)):
            out = [
                int(user_id),
                int(user_vids[i].item()),
                crit,
                round_loss(user_scores[i], 2),
                0 if uncerts is None else round_loss(uncerts[uidx][i], 2),
            ]
            l_out.append(out)

    return l_out
