from solidago import *
from numpy.typing import NDArray
import numpy as np
import matplotlib.pyplot as plt
import scipy

t = TournesolExport.download()
criteria = t.criteria()
t = poll_functions.SimpleUserStats()(t)
t = poll_functions.SimpleEntityStats()(t)
t = poll_functions.SimpleComparisonStats("largely_recommended", criteria)(t)


def _unsquash(values: NDArray[np.float64]):
    values = values.clip(-99.99, 99.99)
    return values / np.sqrt(100.0**2 - values)
t.user_models.user_directs.set_columns(unsquashed_values=_unsquash(t.user_models.user_directs.value))
t.global_model.directs.set_columns(unsquashed_values=_unsquash(t.global_model.directs.value))


def confidence_interval(scores, confidence=0.95):
    mean = scores.mean()
    z_deviation = np.sqrt(2) * scipy.special.erfinv(confidence)
    deviation = z_deviation * np.sqrt( scores.var() / len(scores) )
    return mean - deviation, mean + deviation

def plot_criteria(comparisons, figsize=(2, 3)):
    fig, axs = plt.subplots(3, 3, figsize=figsize)
    for n_plot, ax in enumerate(axs.flat):
        criterion = list(criteria)[n_plot]
        cc = comparisons[comparisons.criteria == criterion]
        ax.hist(cc.score, bins=21)
        ax.set_title(criteria)

def n_extreme_values(scores, n_std_dev):
    mean = scores.mean()
    std_dev = np.sqrt(scores.var())
    return len(scores[np.abs(scores - mean) > n_std_dev * std_dev])
    
def plot(comparison_scores, colors=("g", "y", "r"), labels=None):
    if labels is None:
        plt.hist(comparison_scores, 21, density=True, histtype='bar', color=colors)
    else:
        plt.hist(comparison_scores, 21, density=True, histtype='bar', color=colors, label=labels)
