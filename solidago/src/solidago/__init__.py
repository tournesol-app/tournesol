"""Solidago library, robust and secure algorithms for the Tournesol platform"""

from pathlib import Path
from types import ModuleType
from typing import Any, Type
from inspect import getfullargspec

import yaml

from .__version__ import __version__

from solidago import primitives, poll_functions, generators

from solidago.primitives.datastructure import FilteredTable, NamedObjects
from solidago.poll import *
from solidago.generators import Generator
from solidago.poll_functions import *
from solidago.experiments import *


__all__ = [
    "load",
    "primitives", "poll_functions", "generators", 
    "PollFunction", "Sequential", "Identity", 
    "Generator", 
    "User", "Users", "Entity", "Entities",
    "Vouches",
    "PublicSettings",
    "Rating", "Ratings",
    "Comparison", "Comparisons",
    "VotingRights",
    "Score", "Scores", "ScoringModel", "UserModels",
    "Poll", "TournesolExport",
    "Experiment"
]

LoadedTypes = FilteredTable | NamedObjects | Poll | PollFunction
LoadableType = LoadedTypes | type | Path | str | tuple[str | type, dict[str, Any]] | list[str | type | dict[str, Any]] | dict[str, Any]

def load(classname: LoadableType, base_module: ModuleType | None = None, *args: Any, **kwargs: Any) -> LoadedTypes:
    """ name can either be a filename or the name of an object """
    if isinstance(classname, (FilteredTable, NamedObjects, Poll, PollFunction)):
        return classname
    elif isinstance(classname, Type) and issubclass(classname, (FilteredTable, NamedObjects, Poll, PollFunction)):
        cls = classname
        return cls.load(*args, **kwargs) if hasattr(cls, "load") else cls(*args, **kwargs) # type: ignore
    elif isinstance(classname, (list, tuple)):
        assert len(classname) == 2
        classname, kwargs2 = classname
        assert isinstance(classname, (str, type)) and isinstance(kwargs, dict)
        return load(classname, *args, **(kwargs2 | kwargs)) # type: ignore
    elif isinstance(classname, dict):
        return load(*args, **classname, **kwargs)
    elif isinstance(classname, Path):
        return load(str(classname), *args, **kwargs)
    
    assert isinstance(classname, str)
    if classname.endswith(".yaml"):
        path = "/".join(classname.split("/")[:-1])
        with open(classname) as f:
            return load(yaml.safe_load(f), *args, **kwargs, path=path)
    
    import solidago
    classnames, type_recovery, cls = classname.split("."), True, (base_module or solidago)
    for name in classnames:
        type_recovery = hasattr(cls, name)
        if not type_recovery:
            break
        cls = getattr(cls, name)
    
    if type_recovery:
        f = cls.load if hasattr(cls, "load") else cls
        if "path" in kwargs and "path" not in getfullargspec(f).args:
            del kwargs["path"]
        return f(*args, **kwargs) # type: ignore

    try:
        return Poll.load(classname, *args, **kwargs)
    except FileNotFoundError:
        raise ValueError(f"Cannot load {classname}: Object not known")
