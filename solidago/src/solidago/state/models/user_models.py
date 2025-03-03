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
        default_model_cls: Optional[tuple[str, dict]]=None,
        user_model_cls_dict: Optional[dict[str, tuple]]=None
    ):
        self.user_directs = MultiScore.load(user_directs, 
            key_names=["username", "entity_name", "criterion"],
            name="user_directs"
        )
        self.user_scales = MultiScore.load(user_scales, 
            key_names=["username", "depth", "criterion", "kind"],
            name="user_scales"
        )
        self.common_scales = MultiScore.load(common_scales, 
            key_names=["depth", "criterion", "kind"],
            name="common_scales"
        )
        self.default_model_cls = default_model_cls or ("DirectScoring", dict())
        self.user_model_cls_dict = user_model_cls_dict or dict()
        self._cache_users = None
        self._cache_criteria = None
    
    @classmethod
    def load(cls, kwargs) -> "UserModels":
        return cls(**kwargs)

    def __call__(self, 
        entities: Union[str, "Entity", "Entities"],
        criterion: Optional[str]=None,
    ) -> MultiScore:
        return self.score(entities, criterion)
    
    def score(self, 
        entities: Union[str, "Entity", "Entities"],
        criterion: Optional[str]=None,
    ) -> MultiScore:
        key_names = ["username"]
        from solidago.state.entities import Entities
        if isinstance(entities, Entities):
            key_names.append("entity_name")
        if criterion is None:
            key_names.append("criterion")
        criteria = self.criteria() if criterion is None else { criterion }
        entities = entities if isinstance(entities, Entities) else [entities]
        scores = [ 
            (str(user), str(entity), c, model.score(entity, c)) 
            for user, model in self
            for entity in entities 
            for c in criteria 
        ]
        results = MultiScore(
            data=[(u, e, c, *s.to_triplet()) for u, e, c, s in scores if not s.isnan()],
            key_names=["username", "entity_name", "criterion"]
        )
        results.key_names = key_names
        return results

    def model_cls(self, user: Union[str, "User"]) -> tuple[str, dict]:
        if str(user) in self.user_model_cls_dict:
            return self.user_model_cls_dict[str(user)]
        return self.default_model_cls

    def __getitem__(self, user: Union[str, "User"]) -> ScoringModel:
        import solidago.state.models as models
        constructor_name, kwargs = self.model_cls(user)
        return getattr(models, constructor_name)(
            directs=self.user_directs.get(username=user, cache_group=True), 
            scales=self.user_scales.get(username=user, cache_group=True) \
                | self.common_scales.assign(username=str(user)), 
            username=str(user),
            user_models=self,
            **kwargs
        )
    
    def __delitem__(self, user: Union[str, "User"]) -> None:
        self.user_directs = self.user_directs.delete(username=str(user))
        self.user_scales = self.user_scales.delete(username=str(user))
        if str(user) in self.user_model_cls_dict:
            del self.user_model_cls_dict[str(user)]
        if self._cache_users is not None:
            self._cache_users.remove(str(user))
        self._cache_criteria = None
        
    def __setitem__(self, user: Union[str, "User"], model: ScoringModel) -> None:
        del self[user]
        self.user_directs = self.user_directs | model.directs.assign(username=str(user))
        self.user_scales = self.user_scales | model.scales.assign(username=str(user))
        if not model.is_cls(self.default_model_cls):
            self.user_model_cls_dict[str(user)] = model.save()
        if self._cache_users is not None:
            self._cache_users.add(str(user))
        if self._cache_criteria is not None:
            self._cache_criteria.add(set(model.directs["criterion"]))
    
    def users(self) -> set[str]:
        if self._cache_users is None:
            self._cache_users = set(self.user_directs["username"]) \
                | set(self.user_scales["username"]) \
                | set(self.user_model_cls_dict.keys())
        return self._cache_users

    def __len__(self) -> int:
        return len(self.users())

    def criteria(self) -> set[str]:
        if self._cache_criteria is None:
            self._cache_criteria = set(self.user_directs["criterion"])
        return self._cache_criteria
    
    def __contains__(self, user: Union[str, "User"]) -> bool:
        return str(user) in self.users()
    
    def __iter__(self) -> Iterable:
        for username in self.users():
            yield username, self[username]
    
    def _depth_shifted_scales(self, added_depth: int=1) -> tuple[MultiScore, MultiScore]:
        user_scales_depth = (self.user_scales["depth"].astype(int) + added_depth).astype(str)
        user_scales = type(self.user_scales)(
            data=self.user_scales.assign(depth=user_scales_depth), 
            key_names=self.user_scales.key_names
        )
        common_scales_depth = (self.common_scales["depth"].astype(int) + added_depth).astype(str)
        common_scales = type(self.common_scales)(
            data=self.common_scales.assign(depth=common_scales_depth), 
            key_names=self.common_scales.key_names
        )
        return user_scales, common_scales
    
    def scale(self, scales: MultiScore, note: str="None") -> "UserModels":
        user_scales, common_scales = self._depth_shifted_scales()
        if "depth" not in scales.columns:
            scales["depth"] = "0"
        if "username" in scales.key_names:
            user_scales = user_scales | scales
        else:
            common_scales = common_scales | scales
        return UserModels(
            user_directs=self.user_directs,
            user_scales=user_scales,
            common_scales=common_scales,
            default_model_cls=("ScaledModel", dict(note=note, parent=self.default_model_cls)),
            user_model_cls_dict={
                username: ("ScaledModel", dict(note=note, parent=model_cls))
                for username, model_cls in self.user_model_cls_dict.items()
            }
        )
    
    def post_process(self, cls_name: str, **kwargs) -> "UserModels":
        user_scales, common_scales = self._depth_shifted_scales()
        return UserModels(
            user_directs=self.user_directs,
            user_scales=user_scales,
            common_scales=common_scales,
            default_model_cls=(cls_name, kwargs | dict(parent=self.default_model_cls)),
            user_model_cls_dict={
                username: (cls_name, kwargs | dict(parent=model_cls))
                for username, model_cls in self.user_model_cls_dict.items()
            }
        )
    
    def save_df(self, directory: Union[Path, str], df_name: str) -> str:
        if not getattr(self, df_name).empty:
            getattr(self, df_name).save(directory)
            return f"{directory}/{df_name}.csv"
        return None
    
    def save(self, directory: Union[Path, str], json_dump: bool=False) -> tuple[str, dict]:
        j = type(self).__name__, dict()
        for df_name in ("user_directs", "user_scales", "common_scales"):
            filename = self.save_df(directory, df_name)
            if filename is not None:
                j[1][df_name] = filename
        if self.default_model_cls is not None:
            j[1]["default_model_cls"] = self.default_model_cls
        if len(self.user_model_cls_dict) > 0:
            j[1]["user_model_cls_dict"] = self.user_model_cls_dict
        if json_dump:
            with open(directory / "user_models.json", "w") as f:
                json.dump(j, f)
        return j

    def __repr__(self) -> str:
        return "\n\n".join([
            repr(df) 
            for df in (self.user_directs, self.user_scales, self.common_scales)
        ])
        
