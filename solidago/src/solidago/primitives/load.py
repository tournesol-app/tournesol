from inspect import getfullargspec
from pathlib import Path
from types import ModuleType
from typing import Any, Type, TypeVar
import yaml


T = TypeVar("T")

def load(
    x: Type | list | tuple | Path | str | T | None, 
    base_module: ModuleType | None = None, 
    out_type: Type[T] | None = None,
    default: Type | list | tuple | Path | str | T | None = None,
    *args: Any, **kwargs: Any
) -> T:
    """ name can either be a filename or the name of an object. 
    It is recommended to perform type test on the output to catch loading errors. """
    if x is None:
        return load(default, base_module, out_type, **kwargs)

    if out_type is not None and isinstance(x, out_type):
        return x
    
    if isinstance(x, Type):
        return x.load(*args, **kwargs) if hasattr(x, "load") else x(*args, **kwargs)    
    elif isinstance(x, (list, tuple)):
        assert len(x) == 2
        cls, kwargs2 = x
        assert isinstance(cls, (str, type)) and isinstance(kwargs, dict)
        return load(cls, base_module, out_type, *args, **(kwargs2 | kwargs))
    elif isinstance(x, Path):
        return load(str(x), base_module, out_type, *args, **kwargs)
    
    assert isinstance(x, str), (x, type(x))
    if x.endswith(".yaml"):
        path = "/".join(x.split("/")[:-1])
        with open(x) as f:
            return load(yaml.safe_load(f), base_module, *args, **kwargs, path=path)
    
    import solidago
    classnames, type_recovery, cls = x.split("."), True, (base_module or solidago)
    for name in classnames:
        type_recovery = hasattr(cls, name)
        if not type_recovery:
            break
        cls = getattr(cls, name)
    
    if type_recovery:
        # f = getattr(cls, "load") if hasattr(cls, "load") else cls
        f = cls
        if "path" in kwargs and "path" not in getfullargspec(f).args:
            del kwargs["path"]
        return f(*args, **kwargs) # type: ignore

    raise ValueError(f"Failed load {x} from {base_module} with kwargs={kwargs}")
