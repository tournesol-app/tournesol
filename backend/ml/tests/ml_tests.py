"""
ML test module
"""

import numpy as np
import torch
import gin

from ml.data_utility import (
    rescale_rating, get_all_vids, get_mask,
    reverse_idxs, sort_by_first, expand_dic, expand_tens)
from ml.handle_data import select_criteria, shape_data, distribute_data
from ml.losses import (
    _bbt_loss, _approx_bbt_loss, get_s_loss, round_loss,
    models_dist, models_dist_huber, model_norm)
from ml.metrics import (
    scalar_product, _random_signs, get_uncertainty_glob,
    # check_equilibrium_glob, check_equilibrium_loc,
    get_uncertainty_loc)
from ml.licchavi import Licchavi, get_model, get_s
from ml.core import _set_licchavi, _train_predict, ml_run, HP_PATH


# parse parameters written in "hyperparameters.gin"
gin.parse_config_file(HP_PATH)


TEST_DATA = [
                [1, 100, 101, "test", 100, 0],
                [1, 101, 102, "test", 100, 0],
                [1, 104, 105, "test", 100, 0],
                [0, 100, 101, "test", 0, 0],
                [1, 104, 105, "test", 37, 0],
                [2, 104, 105, "test", 100, 0],
                [7, 966, 965, "test", 4, 0],
                [0, 100, 101, "largely_recommended", 100, 0],
            ]
CRITERIAS = ['test']


def _dic_inclusion(dic1, dic2):
    """ checks if dic1 is included in dic2

    dic1 (dictionnary)
    dic2 (dictionnary)

    Returns:
        (bool): True if a included in b
    """
    return all(item in dic2.items() for item in dic1.items())


# ========== unit tests ===============
# ---------- data_utility.py ----------------
def test_rescale_rating():
    """ unit test """
    assert rescale_rating(100) == 1
    assert rescale_rating(0) == -1


def test_get_all_vids():
    """ unit test """
    size = 50
    input0 = np.reshape(np.arange(4 * size), (size, 4))
    assert len(get_all_vids(input0)) == 2 * size


def test_get_mask():
    """ unit test """
    input1 = torch.randint(2, (5, 4), dtype=bool)  # boolean tensor
    input2 = torch.zeros((5, 4), dtype=bool)
    mask = get_mask(input1, input2)
    assert mask.shape == torch.Size([4])


def test_sort_by_first():
    """ unit test """
    size = 50
    arr = np.reshape(np.array(range(2 * size, 0, -1)), (size, 2))
    arr_sort = sort_by_first(arr)
    # second sort has no effect
    assert (arr_sort == sort_by_first(arr_sort)).all()
    assert isinstance(arr_sort, np.ndarray)  # output is a numpy array


def test_reverse_idx():
    """ unit test """
    size = 20
    vids = np.arange(0, size, 2)
    vid_vidx = reverse_idxs(vids)  # {vid: vidx} dic
    vids2 = np.zeros(size // 2)
    for vid in vids:
        vids2[vid_vidx[vid]] = vid
    assert (vids2 == vids).all()  # output can reconstitute input
    assert isinstance(vid_vidx, dict)  # output is a dictionnary


def test_expand_tens():
    """ unit test """
    len1, len2 = 4, 2
    tens = torch.ones(len1)
    output = expand_tens(tens, len2)
    assert len(output) == len1 + len2  # good final length
    # expanded with zeros and with gradient needed
    assert (output[len1 + 1:] == torch.zeros(len2)).all()
    assert output.requires_grad


def test_expand_dic():
    """ unit test """
    vid_vidx = {100: 0, 200: 2, 300: 1}
    l_vid_new = [200, 500, 700]
    dic_new = expand_dic(vid_vidx, l_vid_new)
    assert _dic_inclusion(vid_vidx, dic_new)  # new includes old
    assert len(dic_new) == 5  # new has good length
    assert (500 in dic_new.keys()) and (700 in dic_new.keys())  # new updated


# -------- handle_data.py -------------
def test_select_criteria():
    """ unit test """
    comparison_data = TEST_DATA
    crit = "test"
    output = select_criteria(comparison_data, crit)
    for comp in output:
        assert len(comp) == 6  # len of each element of output list
    assert isinstance(output, list)
    assert len(output) == len(TEST_DATA) - 1  # number of comparisons extracted


def test_shape_data():
    """ unit test """
    l_ratings = [
        [0, 100, 101, "test", 100, 0],
        [0, 100, 101, "test", 50, 0],
        [0, 100, 101, "test", 0, 0],
    ]
    output = shape_data(l_ratings)
    assert isinstance(output, np.ndarray)
    assert output.shape == (3, 4)   # output shape
    assert np.max(abs(output[:, 3])) <= 1  # range of scores


def test_distribute_data():
    """ unit test """
    arr = np.array([[0, 100, 101, 1],
                    [1, 100, 101, -1],
                    [0, 101, 102, 0],
                    ])
    arr[1][0] = 3  # comparison 1 is performed by user or id 3
    nodes_dic, user_ids, vid_vidx = distribute_data(arr)
    assert len(nodes_dic) == 2  # number of nodes
    assert len(nodes_dic[0][0]) == 2  # number of comparisons for user 0
    assert len(nodes_dic[0][0][0]) == 3  # total number of videos
    assert len(user_ids) == len(nodes_dic)  # number of users
    assert len(vid_vidx) == len(nodes_dic[0][0][0])  # total number of videos


# ------------ losses.py ---------------------
def test_bbt_loss_approx_bbt_loss():
    """ unit test """
    l_t = torch.tensor([-2, -0.5, 0.001, 0.1, 0.3, 10, 50, 0.00001, -0.24])
    l_r = torch.tensor([-1, -0.8, -0.754, -0.2, -0.002, 0, 0.3, 0.564, 1])
    assert abs(_bbt_loss(l_t, l_r) - _approx_bbt_loss(l_t, l_r)) <= 0.0001


def test_get_s_loss():
    """ unit test """
    l_s = [0.4, 0.5, 0.67, 0.88, 0.1, 1.2]
    results = [0.9963, 0.8181, 0.6249, 0.515, 2.3076, 0.5377]
    for s_par, res in zip(l_s, results):
        s_tens = torch.tensor(s_par)
        output = get_s_loss(s_tens).item()
        assert abs(output - res) <= 0.001


def test_models_dist():
    """ unit test """
    model1 = torch.tensor([1, 2, 4, 7])
    model2 = torch.tensor([3, -2, -5, 9.2])
    mask = torch.tensor([True, False, False, True])
    assert models_dist(model1, model2) == 17.2
    assert models_dist(model1, model2, mask=mask) == 4.2


def test_models_dist_huber():
    """ unit test """
    d_param = 1
    model1 = torch.tensor([1, 2, 4, 7])
    model2 = torch.tensor([3, -2, -5, 9.2])
    mask = torch.tensor([True, False, False, True])
    assert round_loss(models_dist_huber(
        model1, model2, strength=d_param), 2
    ) == 13.83
    mask_res = round_loss(models_dist_huber(
        model1, model2, mask=mask, strength=d_param), 2
    )
    assert mask_res == 2.65


def test_model_norm():
    """ unit test """
    model = torch.tensor([1, 2, -4.4, 7])
    assert model_norm(model) == 73.36  # squared l2 norm


# --------- licchavi.py ------------
def test_licchavi_init():
    """ unit test """
    licch = Licchavi(0, {}, "test")
    assert isinstance(licch.lr_loc, (float, int))  # gin applied parameters
    # TODO add more tests here


def test_get_model():
    """ unit test """
    model = get_model(6)
    assert (model == torch.zeros(6)).all()
    assert model.requires_grad


def test_get_s():
    """ unit test """
    s_par = get_s()
    assert s_par.requires_grad is True
    assert s_par.shape == torch.Size([1])


# -------- metrics.py --------------
def test_scalar_product():
    """ unit test """
    l_grad1 = [torch.ones(2), torch.ones(3)]
    l_grad2 = [torch.zeros(2), torch.ones(3)]
    l_grad1[1][1] = 7
    output = scalar_product(l_grad1, l_grad2)
    assert output == 9


def test_random_signs():
    """ unit test """
    rd_tens1 = _random_signs(2, 7)
    rd_tens2 = _random_signs(0.1, 300)
    assert sum(abs(rd_tens1)) == 2 * 7
    assert round(abs(rd_tens2).sum().item(), 5) == 0.1 * 300
    assert sum(rd_tens2) < sum(abs(rd_tens2))


def test_get_uncertainty_glob():
    """ unit test """
    licch, _ = _set_licchavi(TEST_DATA, 'test', verb=-1)
    licch.train_loc(nb_epochs=3, compute_uncertainty=False)
    licch.train_glob(nb_epochs=3, compute_uncertainty=False)
    uncert_glob = get_uncertainty_glob(licch)
    assert isinstance(uncert_glob, torch.Tensor)
    assert len(uncert_glob) == licch.nb_vids
    assert torch.logical_and(uncert_glob > 0, uncert_glob <= 10).all()


def test_get_uncertainty_loc():
    """ unit test """
    licch, _ = _set_licchavi(TEST_DATA, 'test', verb=-1)
    licch.train_loc(nb_epochs=3, compute_uncertainty=False)
    uncert_loc = get_uncertainty_loc(licch)
    assert isinstance(uncert_loc, list)
    assert len(uncert_loc) == licch.nb_nodes
    for node in uncert_loc:
        for uncert in node:
            assert 0 <= uncert <= 10


# def test_check_equilibrium_glob(): # FIXME update eq check to new loss
#     """ checks equilibrium at initialisation """
#     licch, _ = _set_licchavi(TEST_DATA, 'test', verb=-1)
#     equil = check_equilibrium_glob(0.001, licch)
#     assert equil == 1.0
#     assert isinstance(equil, float)


# def test_check_equilibrium_loc():
#     """ checks equilibrium at initialisation """
#     licch, _ = _set_licchavi(TEST_DATA, 'test', verb=-1)
#     equil = check_equilibrium_loc(0.1, licch)
#     assert 0 <= equil <= 1
#     assert isinstance(equil, float)


# --------- core.py ------------
def test_set_licchavi():
    """ unit test """
    licch, users_ids = _set_licchavi(TEST_DATA, 'test')
    assert list(licch.nodes.keys()) == list(users_ids)
    assert licch.lr_glob > 0
    for node in licch.nodes.values():
        assert node.model.requires_grad is True
        assert node.model.sum() == 0
    assert licch.w0_par > 0
    assert licch.global_model.requires_grad is True
    assert licch.global_model.sum() == 0


def test_train_predict():
    """ unit test """
    licch, users_ids = _set_licchavi(TEST_DATA, 'test', verb=-1)
    glob, loc, _ = _train_predict(licch, 1, 1)
    assert len(glob) == len(loc) == 2  # good output shape
    assert len(users_ids) == len(loc[1])  # good nb of users
    for vids, scores in zip(*loc):
        assert len(vids) == len(scores)  # matching lengths
        assert isinstance(vids, np.ndarray)  # type
        assert isinstance(scores, torch.Tensor)  # type


def test_ml_run():
    """ checks that outputs of training have normal length """
    glob_scores, contributor_scores = ml_run(
        TEST_DATA,
        epochs_loc_full=1,
        epochs_glob_full=1,
        criterias=["test"],
        resume=False,
        save=False,
        verb=-1
    )[:2]
    assert len(glob_scores) == 7
    assert len(contributor_scores) == 11


# ======= scores quality tests =============
def _id_score_assert(vid, score, glob):
    """ assert that the video with this -id has this -score """
    if glob[0] == vid:
        assert glob[2] == score


def _some_score_tests(glob_scores, loc_scores):
    """ utility for next test """
    nb_scores = [0, 0, 0, 0]
    for loc in loc_scores:
        assert loc[0] in [0, 1, 2, 3]
        nb_scores[loc[0]] += 1  # counting local scores
    assert nb_scores == [6, 5, 2, 2]
    for glob in glob_scores:
        _id_score_assert(107, 0, glob)
        _id_score_assert(108, 0, glob)
        _id_score_assert(109, 0, glob)
        _id_score_assert(110, 0, glob)
        if glob[0] == 102:  # best rated video
            best = glob[2]
        if glob[0] == 100:  # worst rated video
            worst = glob[2]
        if glob[0] == 200:  # test symetric scores
            sym = glob[2]
    for glob in glob_scores:
        assert worst <= glob[2] <= best
        if glob[0] == 201:
            assert glob[2] == -sym  # test symetric scores


def test_simple_train():
    """ test coherency of results for few epochs and very light data """
    comparison_data = [
                        [1, 101, 102, "test", 100, 0],
                        [2, 100, 101, "largely_recommended", 100, 0],
                        [1, 104, 105, "test", 30, 0],
                        [99, 100, 101, "largely_recommended", 100, 0],
                        [2, 108, 107, "test", 10, 0],
                        [0, 100, 102, "test", 70, 0],
                        [0, 104, 105, "test", 70, 0],
                        [0, 109, 110, "test", 50, 0],
                        [2, 107, 108, "test", 10, 0],
                        [1, 100, 101, "test", 100, 0],
                        [3, 200, 201, "test", 85, 0],
                        ]
    glob_scores, loc_scores = ml_run(
        comparison_data,
        epochs_loc_full=2,
        epochs_glob_full=2,
        criterias=["test"],
        resume=False,
        save=True,  # FIXME change path
        verb=-1
    )[:2]
    _some_score_tests(glob_scores, loc_scores)

    # testing resume mode
    glob_scores2, loc_scores2 = ml_run(
        comparison_data,
        epochs_loc_res=0,
        epochs_glob_res=0,
        criterias=["test"],
        resume=True,  # FIXME change path
        save=True,  # FIXME change path
        verb=-1
    )[:2]
    assert glob_scores == glob_scores2
    assert loc_scores == loc_scores2

    glob_scores, loc_scores = ml_run(
        comparison_data,
        epochs_loc_res=2,
        epochs_glob_res=2,
        criterias=["test"],
        resume=True,
        save=False,  # FIXME change path
        verb=-1
    )[:2]
    _some_score_tests(glob_scores, loc_scores)
