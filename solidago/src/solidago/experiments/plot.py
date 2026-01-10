from functools import reduce
from typing import Iterator, Optional
from pathlib import Path
from matplotlib import pyplot as plt

import numpy as np
import logging

from solidago.experiments.experiment import Experiment
from solidago.poll.base import Poll

logger = logging.getLogger(__name__)


class XYZPlot:
    def __init__(self, 
        source: str, 
        xvarname: str, yvarname: str, zvarname: str,
        data_source: str, path: str,
        run_number: int | str | None = None,
        filename: str = "plot", 
        control_varnames: list[str] | None = None,
        title: str = "", format: str = "pdf",
        xlegend: str = "", ylegend: str = "", zlegend: str = "",
        xmin: Optional[float]=None, xmax: Optional[float]=None, 
        ymin: Optional[float]=None, ymax: Optional[float]=None, 
        vlines: list=[], hlines: list=[], 
        confidence: bool=True, 
        xscale: str="linear", yscale: str="linear",
        fontsize=11, figsize_x=3, figsize_y=3, 
        colors=[ "blue", "red", "green", "orange" , "purple", "black", "darkgreen"],
        linestyles=["-", "--", "-.", ":", "-", "--", ":"],
        *args, **kwargs
    ):
        super().__init__(source, read_only=True)
        self.filename = filename
        self.run_id = XYZPlot.get_run_id(data_source, run_number)
        self.data_source = data_source if self.run_id is None else f"{data_source}_{self.run_id}"
        with open(source) as f:
            kwargs = yaml.safe_load(f)
        source_operation = Experiment.load(f"{path}/{self.data_source}/source.yaml")
        assert isinstance(source_operation, IteratedOperation)
        self.source_operation = source_operation
        self.savepath = self.savepath.parent
        self.xvarname, self.yvarname, self.zvarname = xvarname, yvarname, zvarname
        self.control_varnames = control_varnames or list()
        self.title, self.format = title, format
        self.xlegend, self.ylegend, self.zlegend = xlegend, ylegend, zlegend
        self.xmin, self.xmax, self.ymin, self.ymax = xmin, xmax, ymin, ymax
        self.vlines, self.hlines = vlines, hlines
        self.xscale, self.yscale, self.confidence = xscale, yscale, confidence
        self.fontsize, self.figsize_x, self.figsize_y = fontsize, figsize_x, figsize_y
        self.colors, self.linestyles = colors, linestyles
    
    @staticmethod
    def get_run_id(data_source: str, run_number: int | str | None) -> int | None:
        if run_number is None or run_number == "main":
            return None
        if isinstance(run_number, int):
            return run_number
        assert run_number == "last"
        run_number = 0
        while True:
            path = Path(f"{data_source}_{run_number}")
            if not path.is_dir():
                return run_number - 1
            run_number += 1

    def plot(self, data: dict[int | str, dict[int | str | float, tuple[float, float]]], savename: str | Path):
        """ Plots multiple curves, each given by multiple random seeds """
        plt.figure(figsize=(float(self.figsize_x), float(self.figsize_y)))
        plt.xscale(self.xscale)
        plt.yscale(self.yscale)
        def sum(x, y): return x + y
        def union(x, y): return x | y
        xvals = reduce(union, [v.keys() for v in data.values()], set())
        ymeans = reduce(sum, [[y for y, _ in v.values()] for v in data.values()], list())
        yconfs = reduce(sum, [[y for _, y in v.values()] for v in data.values()], list())
        xmin = np.min(list(xvals)) if self.xmin is None else self.xmin
        xmax = np.max(list(xvals)) if self.xmax is None else self.xmax
        ymin = np.min([y - c for y, c in zip(ymeans, yconfs)]) if self.ymin is None else self.ymin
        ymax = np.max([y + c for y, c in zip(ymeans, yconfs)]) if self.ymax is None else self.ymax
        plt.gca().set_xlim(left=xmin, right=xmax)
        plt.gca().set_ylim(bottom=ymin, top=ymax)

        for z, (zval, color, linestyle) in enumerate(zip(data.keys(), self.colors, self.linestyles)):
            zlegend = f"{zval}{self.zlegend}" if len(data) > 1 else None
            self.zplot(data[zval], zlegend, color, linestyle)
        
        for x in self.vlines:
            plt.axvline(x)
        for y in self.hlines:
            plt.axhline(y)
        
        plt.legend(prop={'size': self.fontsize})
        plt.title(self.title)
        plt.xlabel(self.xlegend, size=self.fontsize)
        plt.ylabel(self.ylegend, size=self.fontsize)
        
        plt.savefig(savename, format=self.format, bbox_inches="tight")
        plt.close()

    def zplot(self, data: dict[int | str | float, tuple[float, float]], zlegend: str | None, color: str, linestyle: str):
        """ Plot a curve, given multiple runs for different seeds
        Args:
            data: list[list[float]]
                data[x][seed] is a list of y_values
        """
        data_list = [[xval, ymean, yconf] for xval, (ymean, yconf) in data.items()]
        xvals, ymeans, yconfs = list(zip(*data_list))
        np_ymeans, np_yconfs = np.array(ymeans), np.array(yconfs)
        plt.plot(xvals, np_ymeans, label=zlegend, linestyle=linestyle, color=color)
        if self.confidence and (np_yconfs**2).sum() > 0:
            ymins, ymaxes = np_ymeans - yconfs, np_ymeans + yconfs
            plt.fill_between(xvals, ymins, ymaxes, alpha=0.1, color=color)

    def run(self, skip: list[list[int]] | None = None):
        control_var_indices = self.control_variable_indices()
        iter = self.iter_control_values(control_var_indices) if control_var_indices else [([], [])]
        for indices, values in iter:
            if values: logger.info(f"Plotting {dict(zip(self.control_varnames, values))}")
            data = self.collect_data(control_var_indices, indices)
            savename = self.get_savename(values)
            self.plot(data, savename)
        logger.info(f"Successfully exported data {self.data_source} to plots in {self.savepath}")
    
    def control_variable_indices(self) -> list[int]:
        def find_index(varname): 
            for i, varnames in enumerate(self.source_operation.varnames):
                if varname in varnames: 
                    return i
            raise ValueError(f"Control variable name {varname} not found")
        return [find_index(varname) for varname in self.control_varnames]

    def iter_control_values(self, control_var_indices: list[int]) -> Iterator[tuple[list[int], list]]:
        ranges = [len(self.source_operation.varname_values[var_index]) for var_index in control_var_indices]
        for indices in IteratedOperation.iter_ranges(ranges):
            values = [self.source_operation.varname_values[var_index][i] for var_index, i in zip(control_var_indices, indices)]
            yield indices, values
    
    def controled_indices_iter(self, control_var_indices: list[int], control_indices: list[int]) -> Iterator[list[int]]:
        ranges = [len(values) for values in self.source_operation.varname_values]
        for indices in IteratedOperation.iter_ranges(ranges):
            if all([indices[i] == control_indices[n] for n, i in enumerate(control_var_indices)]):
                yield indices

    def collect_data(
        self, 
        control_var_indices: list[int], 
        control_indices: list[int],
    ) -> dict[str | int, dict[str | int | float, tuple[float, float]]]:
        """ Returns {z: {x: ymeans, yconfs}} """
        raw_data = self.collect_raw_data(control_var_indices, control_indices)
        return self.raw_data_to_ready_to_plot(raw_data)
    def collect_raw_data(
        self, 
        control_var_indices: list[int], 
        control_indices: list[int],
    ) -> dict[str | int, dict[str | int | float, list[float]]]:
        """ Returns {z: {x: [y]}} """
        raw_data = dict()
        for indices in self.controled_indices_iter(control_var_indices, control_indices):
            z = self.collect_value(self.zvarname, indices)
            x = self.collect_value(self.xvarname, indices) # TODO: Handle xvarname == "history.epoch"
            assert isinstance(x, int)
            raw_data[z] = raw_data[z] if z in raw_data else dict()
            raw_data[z][x] = raw_data[z][x] if x in raw_data[z] else list()
            raw_data[z][x].append(self.collect_value(self.yvarname, indices))
        return raw_data
    @staticmethod
    def raw_data_to_ready_to_plot(
        raw_data: dict[str | int, dict[str | int | float, list[float]]]
    ) -> dict[str | int, dict[str | int | float, tuple[float, float]]]:
        data = dict()
        for zval in raw_data:
            data[zval] = dict()
            for xval in raw_data[zval]:
                yvals = np.array(raw_data[zval][xval])
                conf = 1.96 * yvals.std() / len(yvals)**0.5 if len(yvals) > 1 else 0
                data[zval][xval] = (yvals.mean(), conf)
        return data
        
    def collect_value(self, varname: str, indices: list[int]) -> str | int | float:
        base_yaml = self.source_operation.extract_kwargs(indices)
        if has_in_dict(varname, base_yaml):
            value = get_in_dict(varname, base_yaml)
            assert isinstance(value, (str, int, float))
            return value
        # Value must be retrieved from result yaml
        result_yaml = load_json_yaml(f"{self.source_operation.get_savepath(indices)}.yaml")[1]
        value = get_in_dict(varname, result_yaml)
        assert isinstance(value, (str, int, float))
        return value

    def get_savename(self, control_values: list) -> Path:
        if not control_values:
            return self.savepath / f"{self.filename}.{self.format}"
        filename = "" if self.run_id is None else f"{self.run_id}_"
        filename += "_".join([self.filename] + [str(v) for v in control_values])
        filename += f".{self.format}"
        return self.savepath / filename
