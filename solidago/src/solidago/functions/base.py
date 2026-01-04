from abc import ABC, abstractmethod
from typing import Union, Optional, Any
from pathlib import Path
from pandas import Series

import yaml
import os

from solidago.poll import *


class PollFunction(ABC):
    poll_cls: type=Poll
    
    def __init__(self, max_workers: Optional[int]=None):
        max_workers = (os.cpu_count() - 1) if max_workers is None else max_workers
        self.max_workers = max(1, min(max_workers, os.cpu_count() or 1))
        assert "return" in self.__call__.__annotations__, f"{type(self).__name__} must have a return type"
        for key in self.__call__.__annotations__:
            if key not in ("return", "poll", "save_directory", "seed", "skip_steps"):
                assert key in self.poll_cls.__init__.__annotations__, "" \
                    f"The argument `{key}` of function `main` of PollFunction {type(self).__name__} " \
                    f"must be an attribute of {self.poll_cls.__name__}, which are " \
                    f"{set(self.poll_cls.__init__.__annotations__.keys())}."

    @abstractmethod
    def __call__(self) -> Any:
        return None
    
    def poll2objects_function(self, poll: Poll) -> Any:
        """ Must not modify the poll """
        values = self(poll) if "poll" in self.__call__.__annotations__ else self(**{ 
            key: getattr(poll, key) 
            for key in self.__call__.__annotations__ if key != "return" 
        })
        self.type_check(values, self.__call__.__annotations__)
        return values
    
    def assign(self, result: Poll, value: Any):
        self.type_check(value, self.__call__.__annotations__)
        if isinstance(value, Poll):
            result = value
            return None
        for key, key_type in result.__init__.__annotations__.items():
            if isinstance(value, key_type):
                setattr(result, key, value)
                return None
        if isinstance(value, (list, tuple)):
            for v in value:
                for key, key_type in result.__init__.__annotations__.items():
                    if isinstance(v, key_type):
                        setattr(result, key, v)
        elif isinstance(value, (dict, Series)):
            for key, v in dict(value).items():
                assert isinstance(value, result.__init__.__annotations__[key])
                setattr(result, key, v)

    def poll2poll_function(self, poll: Poll, save_directory: Optional[str]=None) -> Any:
        """ Must not modify the poll """
        if self.__call__.__annotations__["return"] == Poll:
            result = self.poll2objects_function(poll)
        else:
            result = Poll() if poll is None else poll.copy()
            self.assign(result, self.poll2objects_function(poll))
        self.save_result(result, save_directory)
        return result
    
    def type_check(self, value, annotations):
        assert "return" in annotations, "" \
            f"Please carefully specify main result type of `{type(self).__name__}`, " \
            f"whose annotation is currently `{annotations}`"
        assert annotations["return"] != Any, "" \
            f"Return type of `{type(self).__name__}`, " \
            f"whose annotation is currently `{annotations}`," \
            f"must not be `Any`"
        if not hasattr(annotations["return"], "__origin__"):
            assert isinstance(value, annotations["return"]), "" \
                "Please verify type consistency " \
                f"of `{type(self).__name__}`, " \
                f"whose annotation is currently `{annotations}`"
        else:
            for index, return_type in enumerate(annotations["return"].__args__):
                assert isinstance(value[index], return_type), "" \
                    f"Please verify type consistency of returned value number {index} " \
                    f"of `{type(self).__name__}`, " \
                    f"whose annotation is currently `{annotations}`"
    
    def save(self, filename: Optional[Union[str, Path]]=None) -> tuple[str, Optional[Union[dict, list]]]:
        y = type(self).__name__, self.args_save()
        if filename is not None:
            with open(filename, "w") as f:
                yaml.dump(y, f)
        return y
    
    def args_save(self) -> Optional[Union[dict, list]]:
        return { 
            key: value.save() 
            for key, value in self.__dict__.items()
            if isinstance(value, PollFunction) 
        }
    
    def save_result(self, poll: Poll, directory: Optional[str]=None) -> None:
        """ result should be the result of the main function """
        if directory is None:
            return None
        poll.save_objects(type(self).__call__.__annotations__["return"], directory)
        return poll.save_instructions(directory)

    def yaml_keys(self) -> list:
        return list(
            key for key in self.__init__.__annotations__ 
            if key[0] != "_" and hasattr(self, key)
        )

    def __str__(self) -> str:
        return repr(self)
        
    def __repr__(self, n_indents: int=0) -> str:
        def sub_repr(key):
            value = getattr(self, key)
            if key == "modules":
                return ", ".join([v.__repr__(n_indents + 1) for v in value])
            return value.__repr__(n_indents + 1) if isinstance(value, PollFunction) else value
                        
        indent = "\t" * (n_indents + 1)
        last_indent = "\t" * n_indents
        return f"{type(self).__name__}(\n{indent}" + f",\n{indent}".join([
            f"{key}={sub_repr(key)}"  for key in self.yaml_keys()
        ]) + f"\n{last_indent})"

    def to_yaml(self):
        return type(self).__name__, { key: getattr(self, key) for key in self.yaml_keys() }
