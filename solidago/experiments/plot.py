import json

from matplotlib import pyplot as plt
from numpy import sort, mean, std
import numpy as np

def plot_file(data_id):
	with open(f"results/{data_id}.json") as f:
		plot(json.load(f), data_id)	

def plot(data, data_id):
	xlabel = data["hyperparameters"]["xlabel"]
	zlabel = data["hyperparameters"]["zlabel"]
	
	if xlabel == "learn_model_size": xlegend = "Dimension d of the trained model"
	else: xlegend = xlabel
	
	# We collect the x and z values, from the different experiments
	x_values, z_values = set(), set()
	for r in data["results"]:
		for h in r["hyperparameters"]:
			if h == xlabel:
				x_values.add(r["hyperparameters"][h])
			elif zlabel is not None and h == zlabel:
				z_values.add(r["hyperparameters"][h])
	x_values, z_values = list(x_values), list(z_values)
	
	# Finally, we consider different y values, and plot a curve for each of them
	ylabels = ("gradient_norm", "honest_loss", "value")
	ylegends = ("Norm of estimated gradient", "Value of honest loss", "Statistical error")
	titles = ("Convergence of gradient descent", "Loss over honest data", "")
	y_logscales = (False, False, False)
	
	for ylabel, ylegend, title, y_logscale in zip(ylabels, ylegends, titles, y_logscales):
		plot_data = { z: dict() for z in z_values } if zlabel is not None else { 0: dict() }
		for r in data["results"]:	
			x = r["hyperparameters"][xlabel]
			z = r["hyperparameters"][zlabel] if zlabel is not None else 0
			plot_data[z][x] = list()
			for seed_result in r["results"]:
				plot_data[z][x].append(seed_result[ylabel])
		seeds_plot_together(plot_data, title, xlegend, ylegend, zlabel,
			f"results/{data_id}_{ylabel}.pdf", y_logscale)
	
	print("Sucessful plotting")

def seeds_plot_together(data, title="", 
	xlegend=None, ylegend=None, zlabel=None, 
	save_name=None, y_logscale=False, legend=None,
	offset=0, vlines=[], hlines=[], 
	fsize=11, ranges=(None, None), figsize=(5, 5), confidence=True
):
	""" Plots multiple curves, each given by multiple random seeds.
	Args:
		data (dict) 				data[z_value][seed][x_value] yields a y_value
		legends (list[str])	One legend per seeds_curve
		x_values (list[floats])		list of x-coordinates for each curve point
		title (str)					Title of the plot
		xlabel (str)				x-axis label
		ylabel (str)				y-axis label
		save_name (str)			Save file name
		log (bool)					Y-scale in log-scale?
		offset (int)				Do not plot the first offset values
		vlines (list[float])	x-coordinate lines to be drawn
		hlines (list[float])	y-coordinate lines to be drawn
		fsize (int)					Font size
		figsize							Figure size
		confidence					Plot confidence intervals given by different seeds
	"""
	plt.figure(figsize = figsize)
	colors = [ "blue", "red", "green", "orange" , "purple", "black", "darkgreen"]
	linestyles = ["-", "--", "-.", ":", "-", "--", ":"]
	windows = list()
	lines = []
	data_keys = list(data.keys())
	data_keys.sort()
	for z, color, linestyle in zip(data_keys, colors, linestyles):
		if zlabel == "n_poisons": zlegend = f"{z} poisons"
		else: zlegend = z
		line, window = _seeds_plot(data[z], zlegend, color, linestyle, y_logscale, offset, confidence)
		lines.append(line)
		windows.append(window)
	xmin, ymin = min([w[0] for w in windows]), min([w[1] for w in windows])
	xmax, ymax = max([w[2] for w in windows]), max([w[3] for w in windows])
	plt.gca().set_xlim([xmin, xmax])
	plt.gca().set_ylim([ymin, ymax])
	for x in vlines:
		plt.axvline(x)
	for y in hlines:
		plt.axhline(y, color = "red")
	plt.legend(prop={'size': fsize})
	plt.title(title)
	plt.xlabel(xlegend, size=fsize)
	plt.ylabel(ylegend, size=fsize)
	if save_name:
		plt.savefig(save_name, format="pdf", bbox_inches="tight")
	plt.close()

def _seeds_plot(data, z=None, color=None, 
		linestyle=None, y_logscale=False, offset=0, confidence=True):
	""" Plot a curve, given multiple runs for different seeds
	Args:
		data (dict)		data[x_value] is a list of y_values
	"""
	x_values = sort(list(data))[offset:]
	y_values = np.array([mean(data[x]) for x in x_values])
	line = _plot(x_values, y_values, z, linestyle, color, y_logscale)
	if confidence:
		confs = [1.96 * std(data[x]) / len(data[x])**0.5 for x in x_values]
		plt.fill_between(list(x_values), y_values - confs, y_values + confs, alpha=0.1, color=color)
	else:
		confs = [0] * len(x_values)
	window = np.min(x_values), np.min(y_values - confs), np.max(x_values), np.max(y_values + confs)
	return line, window

def _plot(x_values, y_values, z, linestyle, color, y_logscale):
	if z is not None and z != 0:
		if y_logscale:
			return plt.semilogy(x_values, y_values, label=z, linestyle=linestyle, color=color)
		else:
			return plt.plot(x_values, y_values, label=z, linestyle=linestyle, color=color)
	else:
		if y_logscale:
			return plt.semilogy(x_values, y_values, linestyle=linestyle, color=color)
		else:
			return plt.plot(x_values, y_values, linestyle=linestyle, color=color)


