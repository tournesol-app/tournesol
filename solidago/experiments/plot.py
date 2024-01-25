import json
import os
import logging

from matplotlib import pyplot as plt
import numpy as np

logger = logging.getLogger(__name__)


def plot_file(results_filename):
    assert results_filename[-5:] == ".json", "json files only"
    assert os.path.exists(results_filename), f"File {results_filename} does not exist"
    
    with open(results_filename) as results_file:
        results = json.load(results_file)
    
    plot_filename = results_filename[:-5] + ".pdf"
    plot(results, plot_filename)

def plot(results, plot_filename):
    """ Plots multiple curves, each given by multiple random seeds.
    
    Parameters
    ----------
    results: dict
        results["xvalues"]: list[float] 
        results["zvalues"]: list[float]
        results["zlegends"]: list[str]
            One legend per seeds_curve
        results["yvalues"]: list[list[float]] or list[list[list[float]]]
            results["yvalues"][z_index][x_index] either the y-value, 
            or a list of y-values obtained from different random seeds.
        Optionally, we may have the entries
            results["title"]: str
            results["ylegend"]: str
            results["xlegend"]: str
            results["ylogscale"]: bool
                Y-scale in log-scale?
            results["offset"]: int
                Do not plot the first offset values
            results["vlines"]: list[float]
                x-coordinate lines to be drawn
            results["hlines"]: list[float]
                y-coordinate lines to be drawn
            results["fontsize"]: int
                Font size
            results["figsize"]: int
                Figure size
            results["confidence"]: bool
                Plot confidence intervals given by different seeds
            results["window"]: { "xmin": float, "ymin": float, "xmax": float, "ymax": float }
    plot_filename: str
        Save file name
    """
    colors = [ "blue", "red", "green", "orange" , "purple", "black", "darkgreen"]
    linestyles = ["-", "--", "-.", ":", "-", "--", ":"]
    assert len(results["zvalues"]) < min(len(colors), len(linestyles))
    
    defaults = dict(title="", y_legend="", x_legend="", ylogscale=False, offset=0, 
        vlines=[], hlines=[], fontsize=11, ranges=(None, None), figsize=(5, 5), confidence=True)
    for key in defaults:
        if key not in results:
            results[key] = defaults[key]
    
    plt.figure(figsize=results["figsize"])
    has_defined_window = "window" in results
    if not has_defined_window:
        results["window"] = dict(xmin=np.inf, ymin=np.inf, xmax=-np.inf, ymax=-np.inf)
    for index, z in enumerate(results["zvalues"]):
        legend, color, linestyle = results["zlegends"][index], colors[index], linestyles[index]
        _, window = _seeds_plot(results["yvalues"][index], results, legend, color, linestyle)
        if not has_defined_window:
            results["window"]["xmin"] = min(results["window"]["xmin"], window["xmin"])
            results["window"]["ymin"] = min(results["window"]["ymin"], window["ymin"])
            results["window"]["xmax"] = max(results["window"]["xmax"], window["xmax"])
            results["window"]["ymax"] = max(results["window"]["ymax"], window["ymax"])
    
    plt.gca().set_xlim([results["window"]["xmin"], results["window"]["xmax"]])
    plt.gca().set_ylim([results["window"]["ymin"], results["window"]["ymax"]])
    for vline in results["vlines"]:
        plt.axvline(vline)
    for hline in results["hlines"]:
        plt.axhline(hline, color = "red")
    plt.legend(prop={'size': results["fontsize"]})
    plt.title(results["title"])
    plt.xlabel(results["xlegend"], size=results["fontsize"])
    plt.ylabel(results["ylegend"], size=results["fontsize"])
    plt.savefig(plot_filename, format="pdf", bbox_inches="tight")
    plt.close()
    logger.info(f"The results were plotted in file {plot_filename}")

def _seeds_plot(yvalues, results, legend, color, linestyle, alpha_confidence=0.1):
    """ Plot a curve, given multiple runs for different seeds
    
    Parameters
    ----------
    yvalues: list[float] or list[list[float]]
        Either a list of yvalues, or a list of list of yvalues obtained from different random seeds.
    """
    offset = results["offset"]
    xvalues = np.array(results["xvalues"][offset:])
    ymeans = np.array([np.mean(y) for y in yvalues[offset:]])
    
    line = _plot(xvalues, ymeans, legend, linestyle, color, results["ylogscale"])
    if results["confidence"]:
        std_devs = np.array([1.96 * np.std(y) / len(y)**0.5 for y in yvalues[offset:]])
        plt.fill_between(xvalues, ymeans - std_devs, ymeans + std_devs, 
            alpha=alpha_confidence, color=color)
    else:
        confs = [0] * len(x_values)
    window = dict(xmin=xvalues.min(), ymin=(ymeans - std_devs).min(), 
        xmax=xvalues.max(), ymax=(ymeans + std_devs).max())
    return line, window

def _plot(xvalues, yvalues, legend, linestyle, color, ylogscale):
    if legend is not None and legend != 0:
        if ylogscale:
            return plt.semilogy(xvalues, yvalues, label=legend, linestyle=linestyle, color=color)
        else:
            return plt.plot(xvalues, yvalues, label=legend, linestyle=linestyle, color=color)
    else:
        if ylogscale:
            return plt.semilogy(xvalues, yvalues, linestyle=linestyle, color=color)
        else:
            return plt.plot(xvalues, yvalues, linestyle=linestyle, color=color)


