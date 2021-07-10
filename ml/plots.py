import os
TOURNESOL_DEV = bool(int(os.environ.get("TOURNESOL_DEV", 0)))
if TOURNESOL_DEV:  # safety net to ensure pyplot is never loaded in production
    import matplotlib.pyplot as plt
    import numpy as np 

"""
Not used in production, for testing only
Used in "experiments.py"

Main file is "ml_train.py"
"""

INTENS = 0.4
# tuple of dic of label, ordinate legend, filename
METRICS = ({"lab":"fit", "ord": "Training Loss", "f_name": "loss"}, 
           {"lab":"gen", "ord": "Training Loss", "f_name": "loss"}, 
           {"lab":"reg", "ord": "Training Loss", "f_name": "loss"}, 
           {"lab":"l2_dist", "ord": "l2 norm", "f_name": "l2dist"}, 
           {"lab":"l2_norm", "ord": "l2 norm", "f_name": "l2dist"}, 
           {"lab":"grad_sp", "ord": "Scalar Product", "f_name": "grad"}, 
           {"lab":"grad_norm", "ord": "Scalar Product", "f_name": "grad"}
           )

def get_style():
    '''gives different line styles for plots'''
    l = ["-","-.",":","--"]
    for i in range(10000):
        yield l[i % 4]

def get_color():
    '''gives different line colors for plots'''
    l = ["red","green","blue","grey"]
    for i in range(10000):
        yield l[i % 4]

STYLES = get_style() # generator for looping styles
COLORS = get_color()

def title_save(title=None, path=None, suff=".png"):
    ''' add title and save plot '''
    if title is not None:   
        plt.title(title)
    if path is not None:
        plt.savefig(path + suff)

def legendize(y):
    ''' label axis of plt plot '''
    plt.xlabel("Epochs")
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
    var = np.var(arr, axis = 0) 
    low, up = means - var, means + var
    return means, low, up

# ----------- to display multiple accuracy curves on same plot -----------
def add_acc_var(arr, label):
    ''' from array add curve of accuracy '''
    acc = arr[:,3,:]
    means, low, up = means_bounds(acc)
    epochs = range(1, len(means) + 1)
    plt.plot(epochs, means, label=label, linestyle=next(STYLES))
    plt.fill_between(epochs, up, low, alpha=0.4)

# ------------- utility for what follows -------------------------
def plot_var(l_hist, l_idx):
    ''' add curve of asked indexes of history to the plot '''
    arr_hist = np.asarray(l_hist)
    epochs = range(1, arr_hist.shape[2] + 1)
    for idx in l_idx:
        vals = arr_hist[:,idx,:]
        vals_m, vals_l, vals_u = means_bounds(vals)
        style, color = next(STYLES), next(COLORS)
        plt.plot(epochs, vals_m,    label=METRICS[idx]["lab"], 
                                    linestyle=style, 
                                    color=color)
        plt.fill_between(epochs, vals_u, vals_l, alpha=INTENS, color=color)

def plotfull_var(l_hist, l_idx, title=None, path=None, show=False):
    ''' plot metrics asked in -l_idx and save if -path provided '''
    plot_var(l_hist, l_idx)
    idx = l_idx[0]
    legendize(METRICS[idx]["ord"])
    title_save(title, path, suff=" {}.png".format(METRICS[idx]["f_name"]))
    if show: 
        plt.show()
    plt.clf()

# ------- groups of metrics on a same plot -----------
def loss_var(l_hist, title=None, path=None):
    ''' plot losses with variance from a list of historys '''
    plotfull_var(l_hist, [0,1,2], title, path)

def l2_var(l_hist, title=None, path=None):
    '''plot l2 norm of gen model from a list of historys'''
    plotfull_var(l_hist, [3,4], title, path)

def gradsp_var(l_hist, title=None, path=None):
    ''' plot scalar product of gradients between 2 consecutive epochs
        from a list of historys
    '''
    plotfull_var(l_hist, [5,6], title, path)

# plotting all we have
def plot_metrics(l_hist, title=None, path=None):
    '''plot and save the different metrics from list of historys'''  
    loss_var(l_hist, title, path)
    l2_var(l_hist, title, path)
    gradsp_var(l_hist, title, path)
