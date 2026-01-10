from abc import abstractmethod
from copy import deepcopy
from functools import cached_property
from typing import Any, Callable
from solidago.poll import *
from .base import PollFunction


class ParallelizedPollFunction(PollFunction):
    def __init__(self, max_workers: int | None = None):
        super().__init__(max_workers)

    def __call__(self, *args, **kwargs) -> Any:
        kwargs |= {Poll.key_by_type(arg): arg for arg in args}
        variables = self._variables(**self._extract(kwargs, "_variables"))
        nonargs_list = self._nonargs_list(variables, **self._extract(kwargs, "_nonargs_list"))
        args_lists_kwargs = self._extract(kwargs, "_args_lists") | self._extract(kwargs, "_args")
        args_lists = self._args_lists(variables, nonargs_list, **args_lists_kwargs)
        results = ParallelizedPollFunction.threading(self.max_workers, self.thread_function, *args_lists)
        return self._process_results(variables, nonargs_list, results, *args_lists)

    def _extract(self, kwargs: dict, fn_name: str) -> dict:
        annotations = getattr(self, fn_name).__annotations__
        return {k: v for k, v in kwargs.items() if k in annotations}
    
    def annotations(self) -> dict:
        annotations = deepcopy(self._variables.__annotations__)
        annotations |= self._nonargs_list.__annotations__
        annotations |= self._args_lists.__annotations__
        annotations |= self._args.__annotations__
        del annotations["variable"], annotations["variables"], annotations["nonargs_list"]
        annotations["return"] = self._process_results.__annotations__["return"]
        return annotations
    
    @abstractmethod
    def _variables(self, **kwargs) -> list:
        raise NotImplemented
    
    @abstractmethod
    def _args(self, variable: Any, **kwargs) -> list:
        raise NotImplemented
    
    @abstractmethod
    @cached_property
    def thread_function(self) -> Callable:
        raise NotImplemented
    
    @abstractmethod
    def _process_results(self, variables: list, nonargs_list: list, results: list, *args_lists) -> Any:
        raise NotImplemented
    
    def _nonargs_list(self, variables: list, **kwargs) -> list[tuple]:
        return [()] * len(variables)
    
    def _args_lists(self, variables: list, nonargs_list: list, **kwargs) -> list:
        return list(zip(*[
            self._args(variable, *non_args, **kwargs) 
            for variable, non_args in zip(variables, nonargs_list)
        ]))

    def threading(max_workers: int, thread_function: Callable, *args_lists) -> list:
        if max_workers == 1:
            return [thread_function(*args) for args in zip(*args_lists)]
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers) as e:
            return list(e.map(thread_function, *args_lists))
        