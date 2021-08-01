
import os
TOURNESOL_DEV = bool(int(os.environ.get("TOURNESOL_DEV", 0)))  # dev mode
if TOURNESOL_DEV:  # safety net to ensure pyplot is never loaded in production
    import matplotlib.pyplot as plt
    import numpy as np

"""
Not used in production, for testing only
Used in "experiments.py"

Main file is "ml_train.py"
"""

INTENS = 0.4  # intensity of coloration
# tuple of dic of label, ordinate legend, filename
METRICS = {
    "fit": {"lab": "fit", "ord": "Training Loss", "f_name": "loss"},
    "s": {"lab": "s", "ord": "Training Loss", "f_name": "loss"},
    'gen': {"lab": "gen", "ord": "Training Loss", "f_name": "loss"},
    'reg': {"lab": "reg", "ord": "Training Loss", "f_name": "loss"},
    'l2_norm': {"lab": "l2_norm", "ord": "l2 norm", "f_name": "l2norm"},
    'grad_sp': {"lab": "grad_sp", "ord": "Scalar Product", "f_name": "grad"},
    'grad_norm': {
        "lab": "grad_norm", "ord": "Scalar Product", "f_name": "grad"},
    'error_glob': {
        "lab": "error_glob", "ord": 'Error', "f_name": "error_glob"},
    'error_loc': {"lab": "error_loc", "ord": 'Error', "f_name": "error_loc"}
}  # FIXME simplify


def get_style():
    '''gives different line styles for plots'''
    styles = ["-", "-.", ":", "--"]
    for i in range(10000):
        yield styles[i % 4]


def get_color():
    '''gives different line colors for plots'''
    colors = ["red", "green", "blue", "grey"]
    for i in range(10000):
        yield colors[i % 4]


STYLES = get_style()  # generator for looping styles
COLORS = get_color()


def title_save(title=None, path=None, suff=".png"):
    ''' Adds title and saves plot '''
    if title is not None:
        plt.title(title)
    if path is not None:
        plt.savefig(path + suff)


def legendize(y, x="Epochs"):
    ''' Labels axis of plt plot '''
    plt.xlabel(x)
    plt.ylabel(y)
    plt.legend()


def means_bounds(arr):
    '''
    arr: 2D array of values (one line is one run)

    Returns:
    - array of means
    - array of (mean - var)
    - array of (mean + var)
    '''
    means = np.mean(arr, axis=0)
    var = np.var(arr, axis=0)
    low, up = means - var, means + var
    return means, low, up


# ----------- to display multiple accuracy curves on same plot -----------
def add_acc_var(arr, label):
    ''' from array add curve of accuracy '''
    acc = arr[:, 3, :]
    means, low, up = means_bounds(acc)
    epochs = range(1, len(means) + 1)
    plt.plot(epochs, means, label=label, linestyle=next(STYLES))
    plt.fill_between(epochs, up, low, alpha=0.4)


# ------------- utility for what follows -------------------------
def plot_var(l_hist, l_metrics):
    ''' add curve of asked indexes of history to the plot '''
    epochs = range(1, len(l_hist[0]['fit']) + 1)
    for metric in l_metrics:
        vals = np.asarray(
            [hist[metric] for hist in l_hist]
        )
        vals_m, vals_l, vals_u = means_bounds(vals)
        style, color = next(STYLES), next(COLORS)
        plt.plot(epochs, vals_m, label=METRICS[metric]["lab"],
                 linestyle=style, color=color)
        plt.fill_between(epochs, vals_u, vals_l, alpha=INTENS, color=color)


def plotfull_var(l_hist, l_metrics, title=None, path=None, show=False):
    ''' plot metrics asked in -l_metrics and save if -path provided '''
    plot_var(l_hist, l_metrics)
    metric = l_metrics[0]
    legendize(METRICS[metric]["ord"])
    title_save(title, path, suff=" {}.png".format(METRICS[metric]["f_name"]))
    if show:
        plt.show()
    plt.clf()


# ------- groups of metrics on a same plot -----------
def loss_var(l_hist, title=None, path=None):
    ''' plot losses with variance from a list of historys '''
    plotfull_var(l_hist, ['fit', 's', 'gen', 'reg'], title, path)


def l2_var(l_hist, title=None, path=None):
    '''plot l2 norm of gen model from a list of historys'''
    plotfull_var(l_hist, ['l2_norm'], title, path)


def gradsp_var(l_hist, title=None, path=None):
    ''' plot scalar product of gradients between 2 consecutive epochs
        from a list of historys
    '''
    plotfull_var(l_hist, ['grad_sp', 'grad_norm'], title, path)


def error_var(l_hist, title=None, path=None):
    ''' Plots difference between predictions and ground truths
    from a list of historys
    '''
    plotfull_var(l_hist, ['error_glob', 'error_loc'], title, path)


# plotting all the metrics we have
def plot_metrics(l_hist, title=None, path=None):
    '''plot and save the different metrics from list of historys'''
    loss_var(l_hist, title, path)
    l2_var(l_hist, title, path)
    gradsp_var(l_hist, title, path)
    if 'error_glob' in l_hist[0]:
        plotfull_var(l_hist, ['error_glob'], title, path)
        plotfull_var(l_hist, ['error_loc'], title, path)


# histogram
def plot_density(tens, title=None, path=None, name="hist.png"):
    """ Saves histogram of repartition

    tens (tensor): data of which we want repartition
    """
    arr = np.asarray(tens)
    _ = plt.hist(arr, density=False, label=title, bins=40)
    legendize("Number", "Value")
    title_save(title, path, name)
    plt.clf()
