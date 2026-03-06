from inspect import getfullargspec
from pathlib import Path
from types import ModuleType
from typing import Any, Type
import yaml


def load(classname: Any, base_module: ModuleType | None = None, *args: Any, **kwargs: Any) -> Any:
    """ name can either be a filename or the name of an object. 
    It is recommended to perform type test on the output to catch loading errors. """
    from solidago import Poll
    
    if isinstance(classname, Type):
        cls = classname
        return cls.load(*args, **kwargs) if hasattr(cls, "load") else cls(*args, **kwargs) # type: ignore
    elif isinstance(classname, (list, tuple)):
        assert len(classname) == 2
        classname, kwargs2 = classname
        assert isinstance(classname, (str, type)) and isinstance(kwargs, dict)
        return load(classname, base_module, *args, **(kwargs2 | kwargs)) # type: ignore
    elif isinstance(classname, dict):
        return load(*args, base_module, **classname, **kwargs)
    elif isinstance(classname, Path):
        return load(str(classname), base_module, *args, **kwargs)
    elif not isinstance(classname, str):
        return classname
    
    assert isinstance(classname, str), (classname, type(classname))
    if classname.endswith(".yaml"):
        path = "/".join(classname.split("/")[:-1])
        with open(classname) as f:
            return load(yaml.safe_load(f), base_module, *args, **kwargs, path=path)
    
    import solidago
    classnames, type_recovery, cls = classname.split("."), True, (base_module or solidago)
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

    try:
        return Poll.load(classname, *args, **kwargs)
    except (AssertionError, FileNotFoundError):
        raise ValueError(f"Failed load {classname} from {base_module} with kwargs={kwargs}")
