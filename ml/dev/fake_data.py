import random
import numpy as np
from math import exp, sinh
import scipy.stats as st
import logging


# ----------- fake data generation ---------------
def _fake_glob_scores(nb_vid, scale=1):
    """ Creates fake global scores for test

    nb_vid (int): number of videos "generated"
    scale (float): variance of generated global scores

    Returns:
        (float array): fake global scores
    """
    glob_scores = np.random.normal(scale=scale, size=nb_vid)
    return glob_scores


def _fake_loc_scores(distribution, glob_scores, loc_noise):
    """ Creates fake local scores for test

    distribution (int list): list of videos rated by the user
    glob_scores (float array): fake global scores
    w (float): nodes weight
    loc_noise (float): variance/std of local scores noise

    Returns:
        (list of list of couples): (vid, local score) for each video
                                            of each node
    """
    all_idxs = range(len(glob_scores))
    b = loc_noise  # scale of laplace noise
    l_nodes = []
    for nb_vids in distribution:  # for each node
        pick_idxs = random.sample(all_idxs, nb_vids)  # videos rated by user
        noises = np.random.laplace(size=nb_vids, scale=b)  # random noise
        node = [
            (idx, glob_scores[idx] + noise) for idx, noise
            in zip(pick_idxs, noises)
        ]  # list of (video id , video local score)
        l_nodes.append(node)
    return l_nodes


def _fake_s(nb_s, multiple_scales=True):
    ''' Returns random s parameters

    nb_s (int): number of s parameters required
    multiple_scales (bool): wether to draw s parameters or set all to 1

    Returns:
        (float array): random independant s parameters
    '''
    if multiple_scales:
        right = np.random.exponential(0.3, nb_s) + 1  # more than 1
        left = np.maximum(- np.random.exponential(0.08, nb_s) + 1, 0.2)  # less
        choice = np.random.randint(0, 2, nb_s, dtype=bool)
        s_params = np.where(choice, right, left)
    else:
        s_params = np.ones(nb_s)
    return s_params


def _rate_density(r, a, b, s):
    """ Returns density of r knowing a and b

    r (float in [-1, 1]): comparison rate
    a (float): local score of video a
    b (float): local score of video b
    s (float): scaling parameter of user

    Returns:
        (float): density of r knowing a and b
    """
    t = s * (a - b)
    dens = t * exp(-r*t) / (2 * sinh(t))
    return dens


def _get_rd_rate(a, b, s):
    """ Gives a random comparison score

    a (float): local score of video a
    b (float): local score of video b
    s (float): scaling parameter of user

    Returns:
        (float): random comparison score
    """
    class my_pdf(st.rv_continuous):
        def _pdf(self, r):
            return _rate_density(r, a, b, s)
    my_cv = my_pdf(a=-1, b=1, name='my_pdf')
    return my_cv.rvs()


def _unscale_rating(r):
    """ Converts [-1,1] to [0, 100] """
    return (r + 1) * 50


def _fake_comparisons(l_nodes, s_params, dens=0.5, crit="test"):
    """

    l_nodes (list of list of couples): (vid, local score) for each video
                                                            of each node
    s_params (float array): s parameter for each node
    crit (str): criteria of comparisons
    dens (float [0,1[): density of comparisons

    Returns:
        (list of lists): list of all comparisons
                    [   contributor_id: int, video_id_1: int, video_id_2: int,
                        criteria: str, score: float, weight: float  ]
    """
    all_comps = []
    for uid, node in enumerate(l_nodes):  # for each node
        if uid % 50 == 0:
            logging.info(f'Node number {uid}')
        s = s_params[uid]
        nbvid = len(node)
        for vidx1, video in enumerate(node):  # for each video
            nb_comp = int(dens * (nbvid - vidx1))  # number of comparisons
            following_videos = range(vidx1 + 1, nbvid)
            pick_idxs = random.sample(following_videos, nb_comp)
            for vidx2 in pick_idxs:  # for each second video drawn
                r = _get_rd_rate(video[1], node[vidx2][1], s)  # get random r
                rate = _unscale_rating(r)  # rescale to [0, 100]
                comp = [uid, video[0], node[vidx2][0], crit, rate, 0]
                all_comps.append(comp)
    return all_comps


def generate_data(
        nb_vid, nb_users, vids_per_user,
        dens=0.8, scale=0.5, noise=0.1):
    """ Generates fake input data for testing

    nb_vid (int): number of videos
    nb_user (int): number of users
    vids_per_user (int): number of videos rated by each user
    dens (float [0,1[): density of comparisons for each user
    scale (float): variance/std of global scores
    noise (float): variance/std of local scores noise

    Returns:

        (float array): fake global scores
        (list of list of couples): (vid, local score) for each video
                                                    of each node
        (float array): random independant s parameters
        (list of lists): list of all comparisons
            [   contributor_id: int, video_id_1: int, video_id_2: int,
                criteria: "test", score: float, weight: float  ]
    """
    s_params = _fake_s(nb_users)
    distr = [vids_per_user] * nb_users
    glob = _fake_glob_scores(nb_vid, scale=scale)
    logging.info(f'{nb_vid} global scores generated')
    loc = _fake_loc_scores(distr, glob, noise)
    logging .info(f'{vids_per_user} local scores generated per user')
    comp = _fake_comparisons(loc, s_params, dens)
    logging.info(f'{len(comp)} comparisons generated')
    return glob, loc, s_params, comp
