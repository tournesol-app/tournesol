"""Solidago library, robust and secure algorithms for the Tournesol platform"""

from pathlib import Path
from typing import Any, Type
import yaml
from inspect import getfullargspec

from .__version__ import __version__

from solidago import primitives, functions, generators
from solidago.primitives import NestedDict, MultiKeyTable, Objects

from solidago.generators import Generator
from solidago.functions import *
from solidago.poll import *
from solidago.experiments import *


__all__ = [
    "load",
    "primitives", "functions", "generators", 
    "PollFunction", "Sequential", "Identity", 
    "Generator", 
    "NestedDict", "MultiKeyTable",
    "User", "Users", "Entity", "Entities",
    "Vouches",
    "MadePublic", "AllPublic",
    "Assessment", "Assessments",
    "Comparison", "Comparisons",
    "VotingRights",
    "Score", "MultiScore", "ScoringModel", "UserModels",
    "Poll", "TournesolExport",
    "Experiment"
]


LoadableType = MultiKeyTable | Objects | Poll | PollFunction | Type | Path | str | tuple | list | dict

def load(classname: LoadableType, *args, **kwargs) -> Any:
    """ name can either be a filename or the name of an object """
    if isinstance(classname, (MultiKeyTable, Objects, Poll, PollFunction)):
        return classname
    elif isinstance(classname, Type) and issubclass(classname, (MultiKeyTable, Objects, Poll, PollFunction)):
        cls = classname
        return cls.load(*args, **kwargs) if hasattr(cls, "load") else cls(*args, **kwargs)
    elif isinstance(classname, (list, tuple)) and len(classname) == 2:
        classname, kwargs2 = classname
        assert isinstance(classname, (str, Type)) and isinstance(kwargs, dict)
        return load(classname, *args, **(kwargs2 | kwargs))
    elif isinstance(classname, dict):
        return load(*args, **classname, **kwargs)
    elif isinstance(classname, Path):
        return load(str(classname), *args, **kwargs)
    
    if classname.endswith(".yaml"):
        path = "/".join(classname.split("/")[:-1])
        with open(classname) as f:
            yaml_content = yaml.safe_load(f)
        if isinstance(yaml_content, dict):
            return load(*args, **(yaml_content | kwargs), path=path)
        assert isinstance(yaml_content, list), yaml_content
        assert len(yaml_content) == 2, yaml_content
        cls, kwargs2 = yaml_content
        return load(cls, **(kwargs2 | kwargs), path=path)
    
    import solidago
    classnames, type_recovery, cls = classname.split("."), True, solidago
    for name in classnames:
        type_recovery = hasattr(cls, name)
        if not type_recovery:
            break
        cls = getattr(cls, name)
    
    if type_recovery:
        f = cls.load if hasattr(cls, "load") else cls
        if "path" in kwargs and "path" not in getfullargspec(f).args:
            del kwargs["path"]
        return f(*args, **kwargs)
    try:
        return Poll.load(classname)
    except FileNotFoundError:
        raise ValueError(f"Cannot load {classname}: Object not known")
