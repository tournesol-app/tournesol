from abc import abstractmethod
from copy import deepcopy
from typing import Any, Callable

import logging

logger = logging.getLogger(__name__)

from solidago.poll import *
from solidago.primitives.timer import time
from .poll_function import PollFunction


class ParallelizedPollFunction(PollFunction):
    block_parallelization: bool = False

    def __init__(self, max_workers: int | None = None):
        super().__init__(max_workers)
        
    def __call__(self, *args, **kwargs) -> Any:
        with time(logger, f"{type(self).__name__} - Loading data"):
            kwargs |= {Poll.key_by_type(arg): arg for arg in args}
            kwargs |= self._process_kwargs(**self._extract(kwargs, "_process_kwargs"))
            variables = self._variables(**self._extract(kwargs, "_variables"))
            nonargs_kwargs = self._extract(kwargs, "_nonargs") | self._extract(kwargs, "_nonargs_list")
            nonargs_list = self._nonargs_list(variables, **nonargs_kwargs)
            args_lists_kwargs = self._extract(kwargs, "_args_lists") | self._extract(kwargs, "_args")
            args_lists = self._args_lists(variables, nonargs_list, **args_lists_kwargs)
        with time(logger, f"{type(self).__name__} - Parallelized computing"):
            results = ParallelizedPollFunction.threading(self.max_workers, self.thread_function, *args_lists)
        with time(logger, f"{type(self).__name__} - Processing results"):
            process_kwargs = self._extract(kwargs, "_process_results")
            return self._process_results(variables, nonargs_list, results, args_lists, **process_kwargs)

    def _get_max_workers(self):
        return 1 if self.block_parallelization else self.max_workers

    def _extract(self, kwargs: dict, fn_name: str) -> dict:
        annotations = getattr(self, fn_name).__annotations__
        return {k: v for k, v in kwargs.items() if k in annotations}
    
    def annotations(self) -> dict:
        annotations = deepcopy(self._process_kwargs.__annotations__)
        annotations |= self._variables.__annotations__
        annotations |= self._nonargs_list.__annotations__
        annotations |= self._nonargs.__annotations__
        annotations |= self._args_lists.__annotations__
        annotations |= self._args.__annotations__
        assert "variable" in self._nonargs.__annotations__, f"Parallelized {type(self).__name__}._nonargs must have argument 'variable'"
        assert "variables" in self._nonargs_list.__annotations__, f"Parallelized {type(self).__name__}._nonargs_list must have argument 'variables'"
        assert "variable" in self._args.__annotations__, f"Parallelized {type(self).__name__}._args must have argument 'variable'"
        assert "variables" in self._args_lists.__annotations__, f"Parallelized {type(self).__name__}._args_lists must have argument 'variables'"
        assert "nonargs_list" in self._args_lists.__annotations__, f"Parallelized {type(self).__name__}._args_lists must have argument 'nonargs_list'"
        del annotations["variable"], annotations["variables"], annotations["nonargs_list"]
        assert "variables" in self._process_results.__annotations__, f"Parallelized {type(self).__name__}._process_results must have argument 'variables'"
        assert "nonargs_list" in self._process_results.__annotations__, f"Parallelized {type(self).__name__}.nonargs_list must have argument 'nonargs_list'"
        assert "results" in self._process_results.__annotations__, f"Parallelized {type(self).__name__}.results must have argument 'results'"
        assert "return" in self._process_results.__annotations__, f"Parallelized {type(self).__name__}._process_results must have returned type"
        annotations["return"] = self._process_results.__annotations__["return"]
        return annotations
    
    def _process_kwargs(self, **kwargs) -> dict:
        return dict()
    
    @abstractmethod
    def _variables(self, **kwargs) -> list:
        raise NotImplemented
    
    @abstractmethod
    def _args(self, variable: Any, nonargs, **kwargs) -> list:
        raise NotImplemented
    
    @abstractmethod
    def thread_function(self, *args, **kwargs) -> Any:
        raise NotImplemented
    
    @abstractmethod
    def _process_results(self, variables: list, nonargs_list: list, results: list, args_lists: list, **kwargs) -> Any:
        raise NotImplemented
    
    def _nonargs_list(self, variables: list, **kwargs) -> list:
        return [self._nonargs(variable, **kwargs) for variable in variables]
    
    def _nonargs(self, variable: Any, **kwargs) -> Any:
        return ()
    
    def _args_lists(self, variables: list, nonargs_list: list, **kwargs) -> list:
        return list(zip(*[
            self._args(variable, non_args, **kwargs) 
            for variable, non_args in zip(variables, nonargs_list)
        ]))

    def threading(max_workers: int, thread_function: Callable, *args_lists) -> list:
        if max_workers == 1:
            return [thread_function(*args) for args in zip(*args_lists)]
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers) as e:
            return list(e.map(thread_function, *args_lists))
        