from abc import ABC, abstractmethod
from typing import Union, Optional
from pathlib import Path

from solidago.state import State


class StateFunction(ABC):
    @abstractmethod
    def __call__(self, state: State) -> None:
        raise NotImplemented

    @classmethod
    def load(cls, filename: Optional[Union[str, Path, list, dict]]=None) -> "Sequential":
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
        return None

    def __str__(self):
        return type(self).__name__
