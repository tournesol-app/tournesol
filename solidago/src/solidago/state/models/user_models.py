from typing import Union, Optional, Iterable
from pathlib import Path
from pandas import DataFrame
from copy import deepcopy

import pandas as pd
import json
import logging

logger = logging.getLogger(__name__)

from solidago.primitives.timer import time
from .base import ScoringModel
from .score import MultiScore
from .direct import DirectScoring
from .scaled import ScaledModel


class UserModels:
    table_keynames: dict[str, tuple]={
        "user_directs": ("username", "entity_name", "criterion"),
        "user_scales": ("username", "height", "kind", "criterion"),
        "common_scales": ("height", "kind", "criterion"),
    }
    
    def __init__(self, 
        user_directs: Optional[MultiScore]=None,
        user_scales: Optional[MultiScore]=None,
        common_scales: Optional[MultiScore]=None,
        default_model_cls: Optional[tuple[str, dict]]=None,
        user_model_cls_dict: Optional[dict[str, tuple]]=None,
        user_models_dict: Optional[dict[str, ScoringModel]]=None
    ):
        for name, table in zip(self.table_keynames, (user_directs, user_scales, common_scales)):
            setattr(self, name, MultiScore(self.table_keynames[name]) if table is None else table)
        self.default_model_cls = default_model_cls or ("DirectScoring", dict())
        self.user_model_cls_dict = user_model_cls_dict or dict()
        self._cache_users = user_models_dict
    
    def model_cls(self, user: Union[str, "User"]) -> tuple[str, dict]:
        if str(user) in self.user_model_cls_dict:
            return self.user_model_cls_dict[str(user)]
        return deepcopy(self.default_model_cls)

    def criteria(self) -> set[str]:
        return set.union(*[getattr(self, name).keys("criterion") for name in self.table_keynames])
        
    def to_dict(self) -> dict[str, ScoringModel]:
        if self._cache_users is None:
            self._cache_users = dict()
            import solidago.state.models as models
            for username in self.user_directs.keys("username") | self.user_scales.keys("username"):
                constructor_name, kwargs = self.model_cls(username)
                kwargs["directs"] = self.user_directs[username]
                kwargs["scales"] = self.user_scales[username] | self.common_scales
                self._cache_users[username] = getattr(models, constructor_name)(**kwargs)
        return self._cache_users

    def __getitem__(self, user: Union[str, "User"]) -> ScoringModel:
        d = self.to_dict()
        if str(user) in d:
            return d[str(user)]
        constructor_name, kwargs = self.model_cls(str(user))
        import solidago.state.models as models
        return getattr(models, constructor_name)(**kwargs)
    
    def __delitem__(self, user: Union[str, "User"]) -> None:
        if user in self.user_directs:
            del self.user_directs[str(user)]
        if user in self.user_scales:
            del self.user_scales[str(user)]
        if str(user) in self.user_model_cls_dict:
            del self.user_model_cls_dict[str(user)]
        if self._cache_users is not None and str(user) in self._cache_users:
            del self._cache_users[str(user)]
        
    def __setitem__(self, user: Union[str, "User"], model: ScoringModel) -> None:
        del self[str(user)]
        for keys, value in model.get_directs():
            self.user_directs[str(user), *keys] = value
        for keys, value in model.get_scales():
            if keys not in self.common_scales:
                self.user_scales[str(user), *keys] = value
        if not model.is_cls(self.default_model_cls):
            self.user_model_cls_dict[str(user)] = model.save()
        if self._cache_users is not None:
            self._cache_users[str(user)] = model

    def __call__(self, 
        entities: Union[str, "Entity", "Entities"],
        criterion: Optional[str]=None,
    ) -> MultiScore:
        return self.score(entities, criterion)
    
    def score(self, 
        entities: Union[str, "Entity", "Entities"],
        criterion: Optional[str]=None,
    ) -> MultiScore:
        keynames = ["username"]
        from solidago.state.entities import Entities
        keynames += ["entity_name"] if isinstance(entities, Entities) else list()
        keynames += ["criterion"] if criterion is None else list()
        results = MultiScore(keynames)
        for username, model in self:
            scores = model(entities, criterion)
            for keys, score in scores:
                results[username, *keys] = score
        return results

    def __len__(self) -> int:
        return len(self.to_dict())
    
    def __contains__(self, user: Union[str, "User"]) -> bool:
        return str(user) in self.to_dict()
    
    def __iter__(self) -> Iterable:
        for username, model in self.to_dict().items():
            yield username, model
        
    def default_height(self) -> int:
        return ScoringModel.model_cls_height(self.default_model_cls)
    
    def height(self, user: Optional[Union[str, "User"]]=None) -> int:
        if user is None or str(user) not in self.user_model_cls_dict:
            return self.default_height()
        return ScoringModel.model_cls_height(self.user_model_cls_dict[str(user)])
    
    def scale(self, scales: MultiScore, **kwargs) -> "UserModels":
        user_scales, common_scales = self.user_scales.deepcopy(), self.common_scales.deepcopy()
        scaled = UserModels(self.user_directs, user_scales, common_scales)
        if "username" in scales.keynames: # Only update user_scales
            for keys, value in scales:
                keys_kwargs = scales.keys2kwargs(*keys)
                keys_kwargs["height"] = self.height(keys_kwargs["username"]) + 1
                new_keys = tuple(keys_kwargs[kn] for kn in scaled.user_scales.keynames)
                scaled.user_scales[new_keys] = value
        else: # Updates common_scales and user_scales when needed
            for keys, value in scales:
                keys_kwargs = scales.keys2kwargs(*keys)
                keys_kwargs["height"] = self.default_height() + 1
                new_keys = tuple(keys_kwargs[kn] for kn in scaled.common_scales.keynames)
                scaled.common_scales[new_keys] = value
            for username, model_cls in self.user_model_cls_dict.items():
                for keys, value in scales:
                    keys_kwargs = scales.keys2kwargs(*keys)
                    keys_kwargs["username"] = username
                    keys_kwargs["height"] = self.height(username) + 1
                    new_keys = tuple(keys_kwargs[kn] for kn in scaled.user_scales.keynames)
                    scaled.user_scales[new_keys] = value
                user_kwargs = kwargs | {"parent": model_cls}
                scaled.user_model_cls_dict[username] = ("ScaledModel", user_kwargs)
        scaled.default_model_cls = ("ScaledModel", kwargs | {"parent": self.default_model_cls})
        
        scaled._cache_users = dict()
        for username, model in self:
            user_scales = scaled.user_scales[username] | scaled.common_scales
            scaled._cache_users[username] = ScaledModel(model, user_scales)
        return scaled
    
    def post_process(self, cls_name: str, **kwargs) -> "UserModels":
        processed = UserModels(self.user_directs, self.user_scales, self.common_scales)
        for username, model_cls in self.user_model_cls_dict.items():
            processed.user_model_cls_dict[username] = (cls_name, kwargs | {"parent": model_cls})
        processed.default_model_cls = (cls_name, kwargs | {"parent": self.default_model_cls})
        if self._cache_users is not None:
            processed._cache_users = dict()
            for username, model in self:
                import solidago.state.models as models
                processed._cache_users[username] = getattr(models, cls_name)(model, **kwargs)
        return processed
    
    @classmethod
    def load(cls, directory: str, **kwargs) -> "UserModels":
        for name, keynames in cls.table_keynames.items():
            if name in kwargs and isinstance(kwargs[name], str):
                df = pd.read_csv(f"{directory}/{kwargs[name]}", keep_default_na=False)
                kwargs[name] = MultiScore(keynames, df, name=name)
        return cls(**kwargs)

    def save_tables(self, directory: Union[Path, str], table_name: str) -> str:
        if getattr(self, table_name):
            getattr(self, table_name).save(directory, f"{table_name}.csv")
            return f"{table_name}.csv"
        return None
    
    def save(self, directory: Optional[str]=None, json_dump: bool=False) -> tuple[str, dict]:
        for table_name in self.table_keynames:
            filename = self.save_tables(directory, table_name)
        return self.save_instructions(directory, json_dump)
    
    def save_instructions(self, directory: Optional[str]=None, json_dump: bool=False) -> tuple[str, dict]:
        kwargs = { name: f"{name}.csv" for name in self.table_keynames if getattr(self, name) }
        if self.default_model_cls is not None:
            kwargs["default_model_cls"] = self.default_model_cls
        if len(self.user_model_cls_dict) > 0:
            kwargs["user_model_cls_dict"] = self.user_model_cls_dict
        if directory is not None and json_dump:
            with open(Path(directory) / "user_models.json", "w") as f:
                json.dump([type(self).__name__, kwargs], f)
        return type(self).__name__, kwargs
        
    def __repr__(self) -> str:
        return "\n\n".join([repr(getattr(self, table_name)) for table_name in self.table_keynames])
        
