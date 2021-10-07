"""
Module used for testing performances (speed)
(To be improved) # TODO
"""
import timeit
import torch

from ml.core import ml_run, TOURNESOL_DEV
from ml.losses import _approx_bbt_loss, get_fit_loss, get_s_loss
from .fake_data import generate_data


if not TOURNESOL_DEV:
    raise Exception('Dev module called whereas TOURNESOL_DEV=0')


def time_this(func, iterations=1, description=""):
    """ Times a function

    func (None -> None): function to time
    iterations (int): number of iterations to average on
    description (str): name of tested function

    Returns:
        (None): Prints average time for tested function to run
    """
    duration = timeit.Timer(func).timeit(number=iterations)
    avg_duration = duration/iterations
    print(f'On average {description} took {avg_duration} seconds')


# ------ prepare some inputs -----------
nb_vids, nb_users, vids_per_user = 1000, 30, 30
_, _, _, FAKE_COMPS = generate_data(
    nb_vids,
    nb_users,
    vids_per_user,
    dens=0.8
)
T, R = torch.tensor([-2.1]), torch.tensor([-0.8])
S = torch.tensor([0.9])

NB_VIDS, NB_COMPS = 10, 20
MODEL = torch.ones(NB_VIDS, requires_grad=True)
one_hot = [False] * 10
one_hot[2] = True
A_BATCH = torch.tensor([one_hot for _ in range(NB_COMPS)])
B_BATCH = torch.tensor([one_hot for _ in range(NB_COMPS)])
R_BATCH = torch.ones(NB_COMPS)


# ================ test functions =================
def bm_ml_run():
    """ ml_run() benchmark """
    epochs = 10
    _, _, _ = ml_run(
        FAKE_COMPS,
        epochs=epochs,
        criterias=["reliability"],
        resume=False,
        save=False,
        verb=-1,
    )


# --------------- losses.py --------------------
def bm_approx_bbt_loss():
    """ approx_bbt_loss() benchmark """
    _ = _approx_bbt_loss(T, R)


def bm_get_s_loss():
    """ get_s_loss() benchmark """
    _ = get_s_loss(S)


def bm_fit_loss_batch():
    """ get_fit_loss_batch() benchmark """
    _ = get_fit_loss(MODEL, S, A_BATCH, B_BATCH, R_BATCH)


# =========== running tests ==================
if __name__ == '__main__':
    time_this(bm_ml_run, 1, "ml_run()")
    time_this(bm_approx_bbt_loss, 10000, "_approx_bbt_loss()")
    time_this(bm_get_s_loss, 10000, 'get_s_loss()')
    time_this(bm_fit_loss_batch, 100, "fit_loss_batch()")
