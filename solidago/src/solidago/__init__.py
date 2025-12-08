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
]

def load(name: Union[Type, Path, str, tuple, list, dict], *args, **kwargs) -> Any:
    """ name can either be a filename or the name of an object """
    if isinstance(name, Type):
        return name(*args, **kwargs)
    elif isinstance(name, (tuple, list)):
        return load(name[0], *args, **name[1], **kwargs)
    elif isinstance(name, dict):
        return load(*args, **name, **kwargs)
    elif isinstance(name, Path):
        return load(str(name), *args, **kwargs)
    if name.endswith(".yaml"):
        with open(name) as f:
            yaml_content = yaml.safe_load(f)
        path = "/".join(name.split("/")[:-1])
        if isinstance(yaml_content, (list, tuple)):
            clsname, kwargs = yaml_content
            return load(clsname, **kwargs, path=path)
        elif isinstance(yaml_content, str):
            return load(yaml_content, path=path)
        else:
            assert isinstance(yaml_content, dict) and "name" in yaml_content, yaml_content
            return load(*args, **yaml_content, **kwargs, path=path)
    import solidago
    assert hasattr(solidago, name), f"Cannot load {name}: Object not known"
    cls = getattr(solidago, name)
    if hasattr(cls, "load"):
        return getattr(cls, "load")(*args, **kwargs)
    return cls(*args, **kwargs)
