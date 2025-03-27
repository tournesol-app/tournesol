from typing import Union, Optional, Iterable
from pathlib import Path
from pandas import DataFrame
from copy import deepcopy

import pandas as pd
import json

from .base import ScoringModel
from .score import MultiScore
from .direct import DirectScoring


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
            setattr(self, name, table or MultiScore(self.table_keynames[name]))
            getattr(self, name).name = name
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
            del self.user_directs[user]
        if user in self.user_scales:
            del self.user_scales[user]
        if str(user) in self.user_model_cls_dict:
            del self.user_model_cls_dict[str(user)]
        if self._cache_users is not None and str(user) in self._cache_users:
            del self._cache_users[str(user)]
        
    def __setitem__(self, user: Union[str, "User"], model: ScoringModel) -> None:
        del self[user]
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
    
    def scale(self, scales: MultiScore, **kwargs) -> None:
        def add_scales_to(table, height):
            for keys, value in scales:
                keys_kwargs = scales.keys2kwargs(*keys)
                keys_kwargs["height"] = height
                new_keys = tuple(keys_kwargs[kn] for kn in table.keynames)
                table[new_keys] = value
        if "username" in scales.keynames:
            for username in scales.keys("username"):
                add_scales_to(self.user_scales, self.height(username) + 1)
        else:
            add_scales_to(self.common_scales, self.default_height() + 1)
            for username, model_cls in self.user_model_cls_dict.items():
                add_scales_to(self.user_scales, self.height(username) + 1)
                self.user_model_cls_dict[username] = ("ScaledModel", kwargs | {"parent": model_cls})
        assert all({ not isinstance(v, MultiScore) for v in kwargs.values() })
        self.default_model_cls = ("ScaledModel", kwargs | {"parent": self.default_model_cls})
        self._cache_users = None
    
    def post_process(self, cls_name: str, **kwargs) -> None:
        for username, model_cls in self.user_model_cls_dict.items():
            self.user_model_cls_dict[username] = (cls_name, kwargs | {"parent": model_cls})
        self.default_model_cls = (cls_name, kwargs | {"parent": self.default_model_cls})
        self._cache_users = None
    
    @classmethod
    def load(cls, directory: str, **kwargs) -> "UserModels":
        for name, keynames in cls.table_keynames.items():
            if name in kwargs and isinstance(kwargs[name], str):
                df = pd.read_csv(f"{directory}/{kwargs[name]}", keep_default_na=False)
                kwargs[name] = MultiScore(keynames, df, name=name)
        return cls(**kwargs)

    def save_tables(self, directory: Union[Path, str], table_name: str) -> str:
        if getattr(self, table_name):
            getattr(self, table_name).save(directory)
            return f"{table_name}.csv"
        return None
    
    def save(self, directory: Union[Path, str], json_dump: bool=False) -> tuple[str, dict]:
        j = type(self).__name__, dict()
        for table_name in self.table_keynames:
            filename = self.save_tables(directory, table_name)
            if filename is not None:
                j[1][table_name] = filename
        if self.default_model_cls is not None:
            j[1]["default_model_cls"] = self.default_model_cls
        if len(self.user_model_cls_dict) > 0:
            j[1]["user_model_cls_dict"] = self.user_model_cls_dict
        if json_dump:
            with open(directory / "user_models.json", "w") as f:
                json.dump(j, f)
        return j

    def __repr__(self) -> str:
        return "\n\n".join([repr(getattr(self, table_name)) for table_name in self.table_keynames])
        
