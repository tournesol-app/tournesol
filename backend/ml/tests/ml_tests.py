import numpy as np
import torch

from ml.core import _set_licchavi, _train_predict, ml_run
from ml.data_utility import (
    expand_dic,
    expand_tens,
    get_all_vids,
    get_mask,
    rescale_rating,
    reverse_idxs,
    sort_by_first,
)
from ml.dev.fake_data import generate_data
from ml.handle_data import distribute_data, select_criteria, shape_data
from ml.licchavi import Licchavi, get_model, get_s
from ml.losses import _approx_bbt_loss, _bbt_loss, get_s_loss, model_norm, models_dist
from ml.metrics import (
    _random_signs,
    check_equilibrium_glob,
    check_equilibrium_loc,
    extract_grad,
    get_uncertainty_glob,
    get_uncertainty_loc,
    scalar_product,
)

"""
Test module for ml

Main file is "ml_train.py"
"""


TEST_DATA = [
    [1, 100, 101, "test", 10, 0],
    [1, 101, 102, "test", 10, 0],
    [1, 104, 105, "test", 10, 0],
    [0, 100, 101, "test", -10, 0],
    [1, 104, 105, "test", 37/5 - 10, 0],
    [2, 104, 105, "test", 10, 0],
    [7, 966, 965, "test", 4 / 5 - 10, 0],
    [0, 100, 101, "largely_recommended", 10, 0],
]
CRITERIAS = ["test"]


def _dic_inclusion(a, b):
    """checks if a is included in

    a (dictionnary)
    b (dictionnary)

    Returns:
        (bool): True if a included in b
    """
    return all([item in b.items() for item in a.items()])


# ========== unit tests ===============
# ---------- data_utility.py ----------------
def test_rescale_rating():
    assert rescale_rating(10) == 1
    assert rescale_rating(-10) == -1


def test_get_all_vids():
    size = 50
    input = np.reshape(np.arange(4 * size), (size, 4))
    assert len(get_all_vids(input)) == 2 * size


def test_get_mask():
    input = torch.randint(2, (5, 4), dtype=bool)  # boolean tensor
    input2 = torch.zeros((5, 4), dtype=bool)
    mask = get_mask(input, input2)
    assert mask.shape == torch.Size([4])


def test_sort_by_first():
    size = 50
    arr = np.reshape(np.array(range(2 * size, 0, -1)), (size, 2))
    sorted = sort_by_first(arr)
    assert (sorted == sort_by_first(sorted)).all()  # second sort has no effect
    assert isinstance(sorted, np.ndarray)  # output is a numpy array


def test_reverse_idx():
    size = 20
    vids = np.arange(0, size, 2)
    vid_vidx = reverse_idxs(vids)  # {vid: vidx} dic
    vids2 = np.zeros(size // 2)
    for vid in vids:
        vids2[vid_vidx[vid]] = vid
    print(vids, vids2)
    assert (vids2 == vids).all()  # output can reconstitute input
    assert isinstance(vid_vidx, dict)  # output is a dictionnary


def test_expand_tens():
    len1, len2 = 4, 2
    tens = torch.ones(len1)
    output = expand_tens(tens, len2)
    assert len(output) == len1 + len2  # good final length
    # expanded with zeros and with gradient needed
    assert (output[len1 + 1 :] == torch.zeros(len2)).all()
    assert output.requires_grad


def test_expand_dic():
    vid_vidx = {100: 0, 200: 2, 300: 1}
    l_vid_new = [200, 500, 700]
    dic_new = expand_dic(vid_vidx, l_vid_new)
    assert _dic_inclusion(vid_vidx, dic_new)  # new includes old
    assert len(dic_new) == 5  # new has good length
    assert (500 in dic_new.keys()) and (700 in dic_new.keys())  # new updated


# -------- handle_data.py -------------
def test_select_criteria():
    comparison_data = TEST_DATA
    crit = "test"
    output = select_criteria(comparison_data, crit)
    for comp in output:
        assert len(comp) == 6  # len of each element of output list
    assert isinstance(output, list)
    assert len(output) == len(TEST_DATA) - 1  # number of comparisons extracted


def test_shape_data():
    l_ratings = [
        (0, 100, 101, "test", 10, 0),
        (0, 100, 101, "test", 0, 0),
        (0, 100, 101, "test", -10, 0),
    ]
    output = shape_data(l_ratings)
    assert isinstance(output, np.ndarray)
    assert output.shape == (3, 4)  # output shape
    assert np.max(abs(output[:, 3])) <= 1  # range of scores


def test_distribute_data():
    arr = np.array(
        [
            [0, 100, 101, 1],
            [1, 100, 101, -1],
            [0, 101, 102, 0],
        ]
    )
    arr[1][0] = 3  # comparison 1 is performed by user or id 3
    nodes_dic, user_ids, vid_vidx = distribute_data(arr)
    assert len(nodes_dic) == 2  # number of nodes
    assert len(nodes_dic[0][0]) == 2  # number of comparisons for user 0
    assert len(nodes_dic[0][0][0]) == 3  # total number of videos
    assert len(user_ids) == len(nodes_dic)  # number of users
    assert len(vid_vidx) == len(nodes_dic[0][0][0])  # total number of videos


# ------------ losses.py ---------------------
def test_bbt_loss_approx_bbt_loss():
    l_t = torch.tensor([-2, -0.5, 0.001, 0.1, 0.3, 10, 50, 0.00001, -0.24])
    l_r = torch.tensor([-1, -0.8, -0.754, -0.2, -0.002, 0, 0.3, 0.564, 1])
    assert abs(_bbt_loss(l_t, l_r) - _approx_bbt_loss(l_t, l_r)) <= 0.0001


def test_get_s_loss():
    l_s = [0.4, 0.5, 0.67, 0.88, 0.1, 1.2]
    results = [0.9963, 0.8181, 0.6249, 0.515, 2.3076, 0.5377]
    for ss, res in zip(l_s, results):
        s = torch.tensor(ss)
        output = get_s_loss(s).item()
        assert abs(output - res) <= 0.001


def test_models_dist():
    model1 = torch.tensor([1, 2, 4, 7])
    model2 = torch.tensor([3, -2, -5, 9.2])
    mask = torch.tensor([True, False, False, True])
    assert models_dist(model1, model2) == 17.2
    assert models_dist(model1, model2, mask=mask) == 4.2


def test_model_norm():
    model = torch.tensor([1, 2, -4.4, 7])
    assert model_norm(model) == 73.36  # squared l2 norm


# --------- licchavi.py ------------
def test_Licchavi():
    licch = Licchavi(0, {}, "test")
    assert type(licch.lr_node) is float  # default gin applied parameters
    # TODO add more tests here


def test_get_model():
    model = get_model(6)
    assert (model == torch.zeros(6)).all()
    assert model.requires_grad


def test_get_s():
    s = get_s()
    assert s.requires_grad is True
    assert s.shape == torch.Size([1])


# -------- metrics.py --------------
def test_extract_grad():
    model = torch.ones(4, requires_grad=True)
    loss = model.sum() * 2
    loss.backward()
    for a, b in zip(extract_grad(model)[0], torch.ones(4) * 2):
        assert a == b


def test_scalar_product():
    l_grad1 = [torch.ones(2), torch.ones(3)]
    l_grad2 = [torch.zeros(2), torch.ones(3)]
    l_grad1[1][1] = 7
    output = scalar_product(l_grad1, l_grad2)
    assert output == 9


def test_random_signs():
    rd_tens1 = _random_signs(2, 7)
    rd_tens2 = _random_signs(0.1, 300)
    assert sum(abs(rd_tens1)) == 2 * 7
    assert round(abs(rd_tens2).sum().item(), 5) == 0.1 * 300
    assert sum(rd_tens2) < sum(abs(rd_tens2))


def test_get_uncertainty_glob():
    licch, _ = _set_licchavi(TEST_DATA, "test", verb=-1)
    licch.train(3, -1)
    uncert_glob = get_uncertainty_glob(licch)
    assert type(uncert_glob) is torch.Tensor
    assert len(uncert_glob) == licch.nb_vids
    assert torch.logical_and(0 < uncert_glob, uncert_glob <= 10).all()


def test_get_uncertainty_loc():
    licch, _ = _set_licchavi(TEST_DATA, "test", verb=-1)
    licch.train(3, -1)
    uncert_loc = get_uncertainty_loc(licch)
    assert type(uncert_loc) is list
    assert len(uncert_loc) == licch.nb_nodes
    for node in uncert_loc:
        for uncert in node:
            assert 0 <= uncert <= 10


def test_check_equilibrium_glob():
    """checks equilibrium at initialisation"""
    licch, _ = _set_licchavi(TEST_DATA, "test", verb=-1)
    eq = check_equilibrium_glob(0.001, licch)
    assert eq == 1.0


def test_check_equilibrium_loc():
    """checks equilibrium at initialisation"""
    licch, _ = _set_licchavi(TEST_DATA, "test", verb=-1)
    eq = check_equilibrium_loc(0.01, licch)
    assert 0.4 <= eq <= 1


# --------- core.py ------------
def test_set_licchavi():
    licch, users_ids = _set_licchavi(TEST_DATA, "test")
    print(type(users_ids))
    print(np.array(licch.nodes.keys()))
    print(licch.nodes.keys() == users_ids)
    assert list(licch.nodes.keys()) == list(users_ids)
    assert licch.lr_gen > 0
    for node in licch.nodes.values():
        assert node.model.requires_grad is True
        assert node.model.sum() == 0
    assert licch.w0 > 0
    assert licch.global_model.requires_grad is True
    assert licch.global_model.sum() == 0


def test_train_predict():
    licch, users_ids = _set_licchavi(TEST_DATA, "test", verb=-1)
    glob, loc, _ = _train_predict(licch, 1, verb=-1)
    assert len(glob) == len(loc) == 2  # good output shape
    assert len(users_ids) == len(loc[1])  # good nb of users
    for vids, scores in zip(*loc):
        assert len(vids) == len(scores)  # matching lengths
        assert type(vids) == np.ndarray  # type
        assert type(scores) == torch.Tensor  # type


def test_ml_run():
    """checks that outputs of training have normal length"""
    nb_vids, nb_users, vids_per_user = 5, 3, 5
    _, _, _, comps_fake = generate_data(nb_vids, nb_users, vids_per_user, dens=0.999)
    glob_scores, contributor_scores = ml_run(
        comps_fake,
        epochs=1,
        criterias=["test"],
        resume=False,
        save=False,
        verb=-1
    )[:2]
    assert nb_vids <= len(glob_scores) <= vids_per_user
    assert len(contributor_scores) == nb_users * vids_per_user


# ======= scores quality tests =============
def _id_score_assert(id, score, glob):
    """assert that the video with this -id has this -score"""
    if glob[0] == id:
        assert glob[2] == score


def test_simple_train():
    """test coherency of results for few epochs and very light data"""
    comparison_data = [
                        [1, 101, 102, "test", 10, 0],
                        [2, 100, 101, "largely_recommended", 10, 0],
                        [1, 104, 105, "test", 30 /5 -10, 0],
                        [99, 100, 101, "largely_recommended", 10, 0],
                        [2, 108, 107, "test", 10 / 5 - 10, 0],
                        [0, 100, 102, "test", 70 / 5 - 10, 0],
                        [0, 104, 105, "test", 70 / 5 - 10, 0],
                        [0, 109, 110, "test", 0, 0],
                        [2, 107, 108, "test", 10 / 5 - 10, 0],
                        [1, 100, 101, "test", 10, 0],
                        [3, 200, 201, "test", 85 / 5 - 10, 0],
                        ]
    glob_scores, loc_scores = ml_run(
        comparison_data,
        epochs=2,
        criterias=["test"],
        resume=False,
        save=True,  # FIXME change path
        verb=-1
    )[:2]
    nb = [0, 0, 0, 0]
    for loc in loc_scores:
        assert loc[0] in [0, 1, 2, 3]
        nb[loc[0]] += 1  # counting local scores
    assert nb == [6, 5, 2, 2]
    for glob in glob_scores:
        _id_score_assert(107, 0, glob)
        _id_score_assert(108, 0, glob)
        _id_score_assert(109, 0, glob)
        _id_score_assert(110, 0, glob)
        if glob[0] == 102:  # best rated video
            best = glob[2]
        if glob[0] == 100:  # worst rated video
            print(glob)
            worst = glob[2]
        if glob[0] == 200:  # test symetric scores
            sym = glob[2]
    for glob in glob_scores:
        assert worst <= glob[2] <= best
        if glob[0] == 201:
            assert glob[2] == -sym  # test symetric scores

    # testing resume mode
    glob_scores2, loc_scores2 = ml_run(
        comparison_data,
        epochs=0,
        criterias=["test"],
        resume=True,  # FIXME change path
        save=True,  # FIXME change path
        verb=-1
    )[:2]
    assert glob_scores == glob_scores2
    assert loc_scores == loc_scores2

    glob_scores, loc_scores = ml_run(
        comparison_data,
        epochs=2,
        criterias=["test"],
        resume=True,
        save=False,  # FIXME change path
        verb=-1
    )[:2]
    nb = [0, 0, 0, 0]
    for loc in loc_scores:
        assert loc[0] in [0, 1, 2, 3]
        nb[loc[0]] += 1  # counting local scores
    assert nb == [6, 5, 2, 2]
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
