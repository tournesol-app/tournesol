import timeit

import torch

from ml.losses import _approx_bbt_loss, _bbt_loss, get_fit_loss, get_s_loss

from ..core import ml_run
from .fake_data import generate_data

"""
Module used for testing performances (speed)

Main file is "ml_train.py"
"""


def time_this(func, iterations=1, description=""):
    """Times a function

    func (None -> None): function to time
    iterations (int): number of iterations to average on
    description (str): name of tested function

    Returns:
        (None): Prints average time for tested function to run
    """
    duration = timeit.Timer(func).timeit(number=iterations)
    avg_duration = duration / iterations
    print(f"On average {description} took {avg_duration} seconds")


# ------ prepare some inputs -----------
nb_vids, nb_users, vids_per_user = 1000, 30, 30
FAKE_DATA, _, _ = generate_data(nb_vids, nb_users, vids_per_user, dens=0.8)
T, R = torch.tensor([-2.1]), torch.tensor([-0.8])
S = torch.tensor([0.9])

nb_vids = 10
nb_comps = 20
MODEL = torch.ones(nb_vids, requires_grad=True)
one_hot = [False] * 10
one_hot[2] = True
A_BATCH = torch.tensor([one_hot for _ in range(nb_comps)])
B_BATCH = torch.tensor([one_hot for _ in range(nb_comps)])
R_BATCH = torch.ones(nb_comps)


# ================ test functions =================
def bm_ml_run():
    epochs = 10
    _, _ = ml_run(
        FAKE_DATA,
        epochs=epochs,
        criterias=["reliability"],
        resume=False,
        save=False,
        verb=-1,
        gpu=False,
    )


# --------------- losses.py --------------------
def bm_bbt_loss():
    _ = _bbt_loss(T, R)


def bm_approx_bbt_loss():
    _ = _approx_bbt_loss(T, R)


def bm_get_s_loss():
    _ = get_s_loss(S)


def bm_fit_loss_batch():
    _ = get_fit_loss(MODEL, S, A_BATCH, B_BATCH, R_BATCH)


# =========== running tests ==================
if __name__ == "__main__":
    time_this(bm_ml_run, 1, "ml_run()")
    time_this(bm_bbt_loss, 10000, "_bbt_loss()")
    time_this(bm_approx_bbt_loss, 10000, "_approx_bbt_loss()")
    time_this(bm_get_s_loss, 10000, "get_s_loss()")
    time_this(bm_fit_loss_batch, 100, "fit_loss_batch()")
