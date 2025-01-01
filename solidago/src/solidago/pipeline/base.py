from abc import ABC, abstractmethod
from typing import Union, Optional, Any
from pathlib import Path

from solidago.state import *


class StateFunction:
    state_cls: type=State
    
    def __init__(self):
        for key in self.main.__annotations__:
            if key != "return":
                assert key in ("state", "save_directory") or key in self.state_cls.__init__.__annotations__, "" \
                    f"The argument `{key}` of function `main` of StateFunction {type(self).__name__} " \
                    f"must be an attribute of {self.state_cls.__name__}, which are " \
                    f"{set(self.state_cls.__init__.__annotations__.keys())}."
    
    def __call__(self, state: State, save_directory: Optional[str]=None) -> Any:
        """ Must not modify the state """
        value = self.main(**{ 
            key: getattr(state, key) 
            for key in self.main.__annotations__ if key != "return" 
        })
        assert "return" in self.main.__annotations__, "" \
            f"Please carefully specify main result type of `{type(self).__name__}`, " \
            f"whose annotation is currently `{self.main.__annotations__}`"
        assert isinstance(value, self.main.__annotations__["return"]), "" \
            "Please carefully specify main result type and verify type consistency " \
            f"of `{type(self).__name__}`, " \
            f"whose annotation is currently `{self.main.__annotations__}`"
        return value
    
    @abstractmethod
    def main(self) -> Any:
        return None

    @classmethod
    def load(cls, filename: Optional[Union[str, Path, list, dict]]=None) -> "StateFunction":
        if filename is None:
            return cls()
        if isinstance(filename, (str, Path)):
            with open(filename) as f:
                args = json.load(f)
        else:
            args = filename
        import solidago.pipeline as pipeline
        if isinstance(args, list):
            return cls(*[ getattr(pipeline, m[0])(m[1]) for m in args ])
        else:
            assert isinstance(args, dict)
            return cls(**{ key: getattr(pipeline, m[0])(m[1]) for key, m in args.items() })

    def save(self, filename: Optional[Union[str, Path]]=None) -> tuple[str, Optional[Union[dict, list]]]:
        j = type(self).__name__, self.args_save()
        if filename is not None:
            with open(filename, "w") as f:
                json.dump(j, f)
        return j
    
    def args_save(self) -> Optional[Union[dict, list]]:
        return { 
            key: value.save() 
            for key, value in self.__dict__.items()
            if isinstance(value, StateFunction) 
        }
    
    def assign(self, result: State, value: Any):
        assert isinstance(value, self.main.__annotations__["return"]), (type(value), self.main.__annotations__["return"])
        if isinstance(value, State):
            result = value
            return None
        for key, key_type in result.__init__.__annotations__.items():
            if isinstance(value, key_type):
                setattr(result, key, value)
                return None
        if isinstance(value, (list, tuple)):
            for v in value:
                for key, key_type in result.__init__.__annotations__.items():
                    if isinstance(value, key_type):
                        setattr(result, key, v)
        elif isinstance(value, (dict, Series)):
            for key, v in dict(value).items():
                assert isinstance(value, result.__init__.__annotations__[key])
                setattr(result, key, v)

    def save_result(self, result: Any, directory: Optional[Union[str, Path]]=None) -> None:
        """ result should be the result of the main function """
        if directory is None:
            return None
        if isinstance(result, self.state_cls.__init__.__annotations__.values()) and hasattr(result, "save"):
            result.save(directory)
            return None
        if isinstance(result, (list, tuple)):
            for sub_result in result:
                self.save_result(directory)
        if isinstance(result, dict):
            for key, sub_result in result.items():
                assert isinstance(sub_result, self.state_cls.__init__.__annotations__[key])
                getattr(self, key).save(directory)

    def json_keys(self) -> list:
        return list(
            key for key in self.__init__.__annotations__ 
            if key[0] != "_" and hasattr(self, key)
        )

    def __str__(self) -> str:
        return repr(self)
        
    def __repr__(self) -> str:
        return f"{type(self).__name__}(\n\t" + "\n\t".join([
            f"{key}={getattr(self, key)}" for key in self.json_keys()
        ]) + "\n)"

    def to_json(self):
        return type(self).__name__, { key: getattr(self, key) for key in self.json_keys() }
