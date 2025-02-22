from typing import Union, Optional, Iterable
from pathlib import Path
from pandas import DataFrame

import pandas as pd

from .base import ScoringModel
from .score import MultiScore
from .direct import DirectScoring


class UserModels:
    def __init__(self, 
        user_directs: Optional[Union[str, DataFrame, MultiScore]]=None,
        user_scales: Optional[Union[str, DataFrame, MultiScore]]=None,
        common_scales: Optional[Union[str, DataFrame, MultiScore]]=None,
        default_model_cls: tuple[str, dict]=("DirectScoring", None),
        user_model_cls_dict: Optional[dict[str, tuple]]=None
    ):
        self.user_directs = user_directs or MultiScore.load(directs, 
            key_names=["username", "entity_name", "criterion"],
            name="user_directs"
        )
        self.user_scales = user_scales or MultiScore.load(scales, 
            key_names=["username", "depth", "kind", "criterion"],
            name="user_scales"
        )
        self.common_scales = common_scales or MultiScore.load(scales, 
            key_names=["depth", "kind", "criterion"],
            name="common_scales"
        )
        self.default_model_cls = default_model_cls
        self.user_model_cls_dict = user_model_cls_dict or dict()
        self._cache_users = set()

    def __call__(self, entity: Union[str, "Entity", "Entities"]) -> MultiScore:
        return self.score(entity)
    
    def score(self, entity: Union[str, "Entity", "Entities"]) -> MultiScore:
        from solidago.state.entities import Entity, Entities
        if isinstance(entity, (str, Entity)):
            result = MultiScore(key_names=["username", "criterion"])
            for username, model in self:
                for criterion, score in model(entity):
                    result.set(username, criterion, score)
            return result
        assert isinstance(entity, Entities)
        entities = entity
        result = MultiScore(key_names=["username", "entity_name", "criterion"])
        for username, model in self:
            for entity in model.evaluated_entities(entities):
                for criterion, score in model(entity):
                    result.set(username, str(entity), criterion, score)
        return result

    def model_cls(self, user: Union[str, "User"]) -> tuple[str, dict]:
        if str(user) in self.user_model_cls_dict:
            return self.user_model_cls_dict[str(user)]
        return self.default_model_cls

    def __getitem__(self, user: Union[str, "User"]) -> ScoringModel:
        import solidago.state.models as models
        constructor_name, kwargs = self.model_cls(user)
        return models.constructor_name(
            directs=self.directs.get(username=user, cache_group=True), 
            scales=self.scales.get(username=user, cache_group=True), 
            username=str(user),
            user_models=self,
            **kwargs
        )
    
    def __delitem__(self, user: Union[str, "User"]) -> None:
        self.directs = self.directs.delete(username=str(user))
        self.scales = self.scales.delete(username=str(user))
        if str(user) in self.user_model_cls_dict:
            del self.user_model_cls_dict[str(user)]
        if self._cache_users is not None:
            self._cache_users.remove(str(user))
        
    def __setitem__(self, user: Union[str, "User"], model: ScoringModel) -> None:
        del self[user]
        self.directs = self.directs | model.directs.assign(username=str(user))
        self.scales = self.scales | model.scales.assign(username=str(user))
        self.user_model_cls_dict[str(user)] = model.save()
        if self._cache_users is not None:
            self._cache_users.add(str(user))
    
    def users(self) -> set[str]:
        if self._cache_users is None:
            self._cache_users = set(self.directs["username"]) | set(self.scales["username"]) \
                | set(self.user_model_cls_dict.keys())
        return self._cache_users
    
    def __contains__(self, user: Union[str, "User"]) -> bool:
        return str(user) in self.users()
    
    def __iter__(self) -> Iterable:
        for username in self.users():
            yield username, self[username]
    
    def scale(self, 
        mutlipliers: Optional[MultiScore]=None, 
        translations: Optional[MultiScore]=None
    ) -> UserModels:
        scale_key_names = ["username", "depth", "kind", "criterion"]
        multipliers = multipliers or MultiScore(key_names=scale_key_names)
        translations = translations or MultiScore(key_names=scale_key_names)
    
    def save(self, directory: Union[Path, str], json_dump: bool=False) -> tuple[str, dict]:
        assert isinstance(directory, (Path, str)), directory
        j = type(self).__name__, dict()
        if not self.directs.empty:
            j[1]["directs"] = self.directs.to_csv(directory)[1]
        if not self.scales.empty:
            j[1]["scales"] = self.scales.to_csv(directory)[1]
        if self.default_model_cls is not None:
            j[1]["default_model_cls"] = self.default_model_cls
        if len(self.user_model_cls_dict) > 0:
            j[1]["user_model_cls_dict"] = self.user_model_cls_dict
        if json_dump:
            with open(directory / "user_models.json", "w") as f:
                json.dump(j, f)
        return j

    def __repr__(self) -> str:
        return f"{repr(self.directs)}\n\n{repr(self.scales)}"
