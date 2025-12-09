"""Solidago library, robust and secure algorithms for the Tournesol platform"""

from pathlib import Path
from typing import Any, Type

import yaml
from .__version__ import __version__

from solidago.primitives import *
from solidago.poll import *
from solidago.modules import *
from solidago.generators import *

__all__ = [
    "NestedDict", "MultiKeyTable",
    "User", "Users", "Entity", "Entities",
    "Vouches",
    "MadePublic", "AllPublic",
    "Assessment", "Assessments",
    "Comparison", "Comparisons",
    "VotingRights",
    "Score", "MultiScore", "ScoringModel", "UserModels",
    "Poll", "TournesolExport",
    "primitives", "modules", "generators",
    "PollFunction", "Sequential", "Identity", "Generator", 
    "load"
]

def load(classname: Union[Type, Path, str, tuple, list, dict], *args, **kwargs) -> Any:
    """ name can either be a filename or the name of an object """
    if isinstance(classname, Type):
        cls = classname
        return cls.load(*args, **kwargs) if hasattr(cls, load) else cls(*args, **kwargs)
    elif isinstance(classname, dict):
        return load(*args, **classname, **kwargs)
    elif isinstance(classname, Path):
        return load(str(classname), *args, **kwargs)
    if classname.endswith(".yaml"):
        with open(classname) as f:
            yaml_content = yaml.safe_load(f)
        path = "/".join(classname.split("/")[:-1])
        if isinstance(yaml_content, str):
            return load(yaml_content, path=path)
        else:
            assert isinstance(yaml_content, dict) and "name" in yaml_content, yaml_content
            return load(*args, **yaml_content, **kwargs, path=path)
    import solidago
    assert hasattr(solidago, classname), f"Cannot load {classname}: Object not known"
    cls = getattr(solidago, classname)
    return cls.load(*args, **kwargs) if hasattr(cls, load) else cls(*args, **kwargs)
