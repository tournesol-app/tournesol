from pathlib import Path
import shutil, logging
from typing import Iterable

import numpy as np
import yaml

logger = logging.getLogger(__name__)

from solidago.experiments.record import Record


class Experiment:
    """ This class is designed for iteration over hyperparameters """
    def __init__(self, 
        source: str, 
        overwrite: bool, 
        variables: list[str] | list[list[str]] | None = None,
        n_seeds: int | None = 1, # None means run without seed. This implies non-reproducibility!
        n_workers: int = 1,
        **kwargs
    ):
        assert source.endswith(".yaml"), source
        self.overwrite = overwrite
        self.terminated = list()
        self.workingpath =  Path(source[:-5] + "_ongoing")
        self.workingpath.mkdir(parents=True, exist_ok=True)
        self.terminated = Experiment.load_terminated(self.workingpath)
        if self.terminated == "terminated":
            self.delete_working_dir()
        self.overwrite_dialog(source)
        if not (self.workingpath / "source.yaml").is_file(): # create status and source files
            shutil.copy(Path(source), self.workingpath / "source.yaml")
        self.savepath = Experiment.derive_savepath(source[:-5], overwrite)
        self.n_seeds = n_seeds
        self.n_workers = n_workers
        self.record = Record(kwargs)
        self.varnames, self.varname_values = self.record.parse_variables(variables)

    def overwrite_dialog(self, source):
        # Handles overwrite issues
        if not (self.workingpath / "source.yaml").is_file():
            return
        with open(source) as f:
            source_content = "\n".join(f.readlines())
        with open(self.savepath / "source.yaml") as f:
            target_source_content = "\n".join(f.readlines())
        if source_content == target_source_content:
            return
        answer = input("The source file does not match the ongoing run. Ignore new source and finish previous run? [y/N] ")
        if answer == "y":
            from solidago import load
            load(self.savepath / "source.yaml", source=source).run()
            self.terminated = "terminated"
        else:
            answer = input("Overwrite previous run? [Y/n] ")
            if answer == "n":
                raise KeyboardInterrupt("Experiments interrupted by the user")
            self.delete_ongoing_files()
    def load_terminated(workingpath) -> list[list[int]] | str:
        path = workingpath / "terminated_iterations.yaml"
        if not path.is_file():
            path.touch()
            return list
        terminated = list()
        line_len = None
        with open(path) as file:
            while True:
                line = file.readline()
                if line == "terminated":
                    return "terminated"
                if not line:
                    return terminated
                iteration = line.split(",")
                terminated.append(iteration)
                if line_len:
                    assert line_len == len(iteration)
                else:
                    line_len = len(iteration)
    def delete_working_dir(self):
        assert str(self.workingpath).endswith("_ongoing")
        for file in self.workingpath.iterdir():
            # For security reasons, we only allow the removal of files of a folder
            # if all files of the folder are of the expected kind
            assert str(file).endswith(".pt") or str(file).endswith(".yaml")
        for file in self.workingpath.iterdir():
            file.unlink()
    def derive_savepath(source_dirpath: str, overwrite: bool) -> Path:
        if overwrite:
            return Path(source_dirpath)
        run_number = 0
        while True:
            path = Path(f"{source_dirpath}_{run_number}")
            if not path.is_dir():
                return path
            run_number += 1


    def run(self):
        logger.info(f"{self.__class__.__name__} {self.savepath}")
        for indices in self.iter_indices():
            self._run_indices(indices)
        logger.info(f"Successful {self.__class__.__name__} {self.savepath}.")
        self.terminate()

    def _run_indices(self, indices: list[int]):
        kwargs = self.extract_kwargs(indices)
        savepath = self.get_savepath(indices)
        self.run_single(savepath, **kwargs)
        self.terminate_iteration(indices)

    def clear_status(self):
        with open(self.savepath / "status.yaml", "w") as f:
            yaml.safe_dump(list(), f)
    def terminate(self):
        with open(self.savepath / "status.yaml", "w") as f:
            yaml.safe_dump("terminated", f)
        super().terminate()
    def terminate_iteration(self, indices: list[int]):
        if isinstance(self.terminated, str):
            return self.terminate()
        self.terminated.append(indices)
        ranges = [len(values) for values in self.varname_values]
        total = np.prod(ranges)
        logger.info(f"Advancement: {len(self.terminated)} indices terminated out of {total}")
        with open(self.savepath / "status.yaml", "w") as f:
            yaml.safe_dump(self.terminated, f)

    def get_savepath(self, indices: list[int]) -> Path:
        filename = "_".join([str(value[index]) for index, value in zip(indices, self.varname_values)])
        return self.savepath / filename
    
    @abstractmethod
    def run_single(self, savepath: Path, **kwargs):
        raise NotImplemented

    @staticmethod
    def iter_ranges(ranges: list[int], skip: list[list[int]] | None = None) -> Iterable[list[int]]:
        skip = skip or list()
        assert all([isinstance(s, list) for s in skip]), skip
        assert all([len(s) == len(ranges) for s in skip]), (ranges, skip)
        if len(ranges) == 1:
            for index in range(ranges[0]):
                yield [index]
            return None
        for first_index in range(ranges[0]):
            subterminated = [s[1:] for s in skip if s[0] == first_index]
            for other_indices in Experiment.iter_ranges(ranges[1:], subterminated):
                indices = [first_index] + other_indices
                if indices not in skip:
                    yield indices
    def iter_indices(self) -> Iterable[list[int]]:
        if self.terminated == "terminated":
            return
        assert isinstance(self.terminated, list)
        ranges = [len(values) for values in self.varname_values]
        for indices in Experiment.iter_ranges(ranges, self.terminated):
            yield indices
    def iter_kwargs(self) -> Iterable[dict]:
        for indices in self.iter_indices():
            yield self.extract_kwargs(indices)
    
    def fail_fast(self):
        for indices in self.iter_indices():
            self.fail_fast_at_indices(indices)
            
    @abstractmethod
    def fail_fast_at_indices(self, indices: list[int]):
        raise NotImplemented
    
    @staticmethod
    def parse_values(values: str | int | list | dict | None):
        if isinstance(values, str) and values.startswith("range("):
            return list(range(int(values[6:-1])))
        return values
        
    def extract_kwargs(self, indices: list[int]) -> dict:
        return extract_indices(self.varnames, self.varname_values, indices, self.kwargs)
