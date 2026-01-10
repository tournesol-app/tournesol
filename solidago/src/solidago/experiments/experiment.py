from pathlib import Path
from typing import Iterable
import shutil, logging

import numpy as np
import yaml

logger = logging.getLogger(__name__)

from solidago.primitives.instructions import Instructions
from solidago.poll import Poll
from solidago.functions import PollFunction, Sequential
from solidago.generators import Generator


class Experiment:
    """ This class is designed for iteration over hyperparameters """
    def __init__(self, 
        source: str, 
        overwrite: bool = False, 
        reproducibility: bool = True, 
        variables: list[str] | list[list[str]] | None = None,
        max_workers: int = 1,
        ignore_ongoing_run: bool | None = None,
        poll: str | dict | None = None,
        generator: list | None = None,
        functions: list | None = None,
    ):
        assert source.endswith(".yaml"), source
        self.overwrite = overwrite
        self.reproducibility = reproducibility
        self.workingpath =  Path(source[:-5] + "_ongoing")
        self.savepath = Experiment.derive_savepath(source[:-5], overwrite)
        self.overwrite_dialog(source, ignore_ongoing_run)
        self.workingpath.mkdir(parents=True, exist_ok=True)
        self.terminated = Experiment.load_terminated(self.workingpath)
        if not (self.workingpath / "source.yaml").is_file(): # create status and source files
            shutil.copy(Path(source), self.workingpath / "source.yaml")
        self.max_workers = max_workers
        self.poll = poll
        self.generator = generator or list()
        self.functions = functions or list()
        self.varnames, self.varname_values = self._instructions().parse_variables(variables)
        self.fail_fast()
    def _instructions(self) -> Instructions:
        return Instructions(dict(poll=self.poll, generator=self.generator, functions=self.functions))
    @classmethod
    def load(cls, source: str, ignore_ongoing_run: bool | None = None, **kwargs):
        with open(source) as f:
            kwargs = yaml.safe_load(f) | kwargs
        return cls(source=source, ignore_ongoing_run=ignore_ongoing_run, **kwargs)        

    def overwrite_dialog(self, source: str, ignore_ongoing_run: bool | None):
        # Handles overwrite issues
        if not (self.workingpath / "source.yaml").is_file():
            return
        if ignore_ongoing_run == True:
            Experiment.safe_directory_deletion(self.workingpath)
            return
        with open(source) as f:
            source_content = "\n".join(f.readlines())
        with open(self.workingpath / "source.yaml") as f:
            target_source_content = "\n".join(f.readlines())
        if source_content == target_source_content:
            return
        if ignore_ongoing_run == False:
            from solidago import load
            load(self.workingpath / "source.yaml", source=source)()
            return
        assert ignore_ongoing_run is None
        answer = input("The source file does not match the ongoing run. Ignore new source and finish previous run? [y/N] ")
        if answer == "y":
            from solidago import load
            load(self.workingpath / "source.yaml", source=source)()
        else:
            answer = input("Overwrite previous run? [Y/n] ")
            if answer == "n":
                raise KeyboardInterrupt("Experiments interrupted by the user")
            Experiment.safe_directory_deletion(self.workingpath)
    def load_terminated(workingpath: Path) -> list[list[int]] | str:
        path = workingpath / "terminated_iterations.yaml"
        if not path.is_file():
            path.touch()
            return list()
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
    def safe_directory_deletion(path: Path):
        if not path.is_dir():
            return
        for file in path.rglob("*"):
            # For security reasons, we only allow the removal of files of a folder
            # if all files of the folder are of the expected kind
            if file.is_file():
                assert str(file).endswith((".pt", ".yaml", ".json", ".csv")), file
        for sub in path.iterdir():
            if sub.is_file():
                sub.unlink()
            else:
                Experiment.safe_directory_deletion(sub)
        path.rmdir()        
    def derive_savepath(source_dirpath: str, overwrite: bool) -> Path:
        if overwrite:
            return Path(source_dirpath)
        run_number = 0
        while True:
            path = Path(f"{source_dirpath}_{run_number}")
            if not path.is_dir():
                return path
            run_number += 1

    def __call__(self):
        logger.info(f"{self.__class__.__name__} {self.workingpath}")
        for indices in self.iter_indices():
            self._run_indices(indices)
        self.terminate()
        logger.info(f"Successful {self.__class__.__name__} {self.savepath}.")
    def _run_indices(self, indices: list[int]):
        poll, generator, functions = self.extract_poll_generator_functions(indices)
        working_savepath = self.get_working_subpath(indices)
        poll = generator(poll, working_savepath)
        poll = functions.poll2poll_function(poll, working_savepath)
        self.terminate_iteration(indices)

    def clear_status(self):
        with open(self.savepath / "terminated_iterations.yaml", "w") as f:
            yaml.safe_dump(list(), f)
    def terminate(self):
        with open(self.workingpath / "terminated_iterations.yaml", "w") as f:
            yaml.safe_dump("terminated", f)
        Experiment.safe_directory_deletion(self.savepath)
        self.workingpath.rename(self.savepath)

    def terminate_iteration(self, indices: list[int]):
        if isinstance(self.terminated, str):
            return self.terminate()
        self.terminated.append(indices)
        ranges = [len(values) for values in self.varname_values]
        total = int(np.prod(ranges))
        logger.info(f"Advancement: {len(self.terminated)} indices terminated out of {total}")
        with open(self.savepath / "terminated_iterations.yaml", "w") as f:
            yaml.safe_dump(self.terminated, f)
    
    def get_working_subpath(self, indices: list[int]) -> Path:
        args = [str(value[index]) for index, value in zip(indices, self.varname_values)]
        subdir_name = "_".join(args)
        return self.workingpath / subdir_name
    
    @staticmethod
    def iter_ranges(ranges: list[int], skip: list[list[int]] | None) -> Iterable[list[int]]:
        skip = skip or list()
        assert all([isinstance(s, list) for s in skip]), skip
        assert all([len(s) == len(ranges) for s in skip]), (ranges, skip)
        if len(ranges) == 0:
            yield list()
            return None
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
        assert isinstance(self.terminated, list), self.terminated
        ranges = [len(values) for values in self.varname_values]
        for indices in Experiment.iter_ranges(ranges, self.terminated):
            yield indices
    def iter_kwargs(self) -> Iterable[dict]:
        for indices in self.iter_indices():
            yield self.extract_kwargs(indices)
    
    def fail_fast(self):
        for indices in self.iter_indices():
            _, _, _ = self.extract_poll_generator_functions(indices)
    
    @staticmethod
    def parse_values(values: str | int | list | dict | None):
        if isinstance(values, str) and values.startswith("range("):
            return list(range(int(values[6:-1])))
        return values
        
    def extract_poll_generator_functions(self, indices: list[int]) -> tuple[Poll, Generator, PollFunction]:
        kwargs = self._instructions().extract_indices(self.varnames, self.varname_values, indices)
        poll = Poll.load(kwargs["poll"])
        generator = Generator(**kwargs["generator"], max_workers=self.max_workers)
        functions = Sequential(modules=kwargs["functions"], max_workers=self.max_workers)
        return poll, generator, functions
