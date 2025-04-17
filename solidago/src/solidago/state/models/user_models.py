from typing import Union, Optional, Iterable
from pathlib import Path
from pandas import DataFrame
from copy import deepcopy
from concurrent.futures import ProcessPoolExecutor, as_completed

import pandas as pd
import json
import logging

logger = logging.getLogger(__name__)

from solidago.primitives.timer import time
from solidago.state.users import User, Users
from .scoring_model import ScoringModel
from .score import Score, MultiScore


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
        default_composition: tuple[str, dict]=[("direct", {})],
        user_composition: Optional[dict[str, tuple]]=None,
        user_models_dict: Optional[dict[str, ScoringModel]]=None,
    ):
        for name, table in zip(self.table_keynames, (user_directs, user_scales, common_scales)):
            setattr(self, name, MultiScore(self.table_keynames[name], name=name) if table is None else table)
        self.default_composition = default_composition
        self.user_composition = user_composition or dict()
        self._cache_users = user_models_dict
    
    def get_composition(self, user: Union[int, str, "User"]) -> tuple[str, dict]:
        username = user.name if isinstance(user, User) else user
        if username in self.user_composition:
            return self.user_composition[username]
        return deepcopy(self.default_composition)

    def criteria(self) -> set[str]:
        return set.union(*[getattr(self, name).keys("criterion") for name in self.table_keynames])
        
    def to_dict(self) -> dict[str, ScoringModel]:
        if self._cache_users is None:
            self._cache_users = dict()
            for username in self.user_directs.keys("username") | self.user_scales.keys("username"):
                self._cache_users[username] = ScoringModel(
                    self.get_composition(username),
                    self.user_directs[username],
                    self.user_scales[username] | self.common_scales
                )
        return self._cache_users

    def __getitem__(self, user: Union[str, "User"]) -> ScoringModel:
        username = user.name if isinstance(user, User) else user
        d = self.to_dict()
        return d[username] if username in d else ScoringModel(self.get_composition(username))
    
    def __delitem__(self, user: Union[str, "User"]) -> None:
        username = user.name if isinstance(user, User) else user
        if user in self.user_directs:
            del self.user_directs[username]
        if user in self.user_scales:
            del self.user_scales[username]
        if username in self.user_composition:
            del self.user_composition[username]
        if self._cache_users is not None and username in self._cache_users:
            del self._cache_users[username]
        
    def __setitem__(self, user: Union[str, "User"], model: ScoringModel) -> None:
        username = user.name if isinstance(user, User) else user
        del self[username]
        for keys, value in model.directs:
            self.user_directs[username, *keys] = value
        for keys, value in model.scales:
            if keys not in self.common_scales:
                self.user_scales[username, *keys] = value
        if not model.matches_composition(self.default_composition):
            self.user_composition[username] = model.save()
        if self._cache_users is not None:
            self._cache_users[username] = model

    def __call__(self, 
        entities: Union[str, "Entity", "Entities", type]=all,
        criteria: Union[str, set, type]=all,
        n_sampled_entities_per_user: Optional[int]=None,
        max_workers: int=1,
    ) -> MultiScore:
        return self.score(entities, criteria, n_sampled_entities_per_user, max_workers)
    
    def score(self, 
        entities: Union[str, "Entity", "Entities", type]=all, 
        criteria: Union[str, set, type]=all,
        n_sampled_entities_per_user: Optional[int]=None,
        max_workers: int=1,
    ) -> MultiScore:
        if max_workers == 1:
            return type(self)._score(self, entities, criteria, n_sampled_entities_per_user)
        batches = [list() for _ in range(max_workers)]
        for index, (username, model) in enumerate(self):
            batches[index % max_workers].append((username, model))
        args = entities, criteria, n_sampled_entities_per_user
        from concurrent.futures import ProcessPoolExecutor, as_completed
        with ProcessPoolExecutor(max_workers=max_workers) as e:
            futures = {e.submit(UserModels._score, batch, *args) for batch in batches}
            batch_results = [f.result() for f in as_completed(futures)]
        results = MultiScore(next(iter(batch_results)).keynames)
        for result in batch_results:
            results |= result
        return results
    
    def _score(
        user_models: Union["UserModels", list[tuple[str, ScoringModel]]], 
        entities: Union[str, "Entity", "Entities", type]=all, 
        criteria: Union[str, set, type]=all,
        n_sampled_entities_per_user: Optional[int]=None,
    ) -> MultiScore:
        keynames = ["username"]
        from solidago.state.entities import Entities
        keynames += ["entity_name"] if isinstance(entities, Entities) or entities is all else list()
        keynames += ["criterion"] if isinstance(criteria, set) or criteria is all else list()
        results = MultiScore(keynames)
        for username, model in user_models:
            for keys, score in model(entities, criteria, n_sampled_entities_per_user):
                results[username, *keys] = score
        return results

    def __len__(self) -> int:
        if self._cache_users is None:
            try:
                return len(set(self.user_directs.init_data["username"]))
            except TypeError:
                return len(self.to_dict())
        return len(self.to_dict())
    
    def __contains__(self, user: Union[str, "User"]) -> bool:
        username = user.name if isinstance(user, User) else user
        return username in self.to_dict()
    
    def __iter__(self) -> Iterable:
        for username, model in self.to_dict().items():
            yield username, model
        
    def default_height(self) -> int:
        return len(self.default_composition)
    
    def height(self, user: Optional[Union[str, "User"]]=None) -> int:
        username = user.name if isinstance(user, User) else user
        if username is None or username not in self.user_composition:
            return self.default_height()
        return len(self.user_composition[username])
    
    def scale(self, scales: MultiScore, note: str="scale", **kwargs) -> "UserModels":
        user_scales, common_scales = self.user_scales.deepcopy(), self.common_scales.deepcopy()
        default_composition = self.default_composition + [("scale", dict(note=note))]
        scaled = UserModels(self.user_directs, user_scales, common_scales, default_composition)
        
        if "username" in scales.keynames: # Only update user_scales
            for keys, value in scales:
                keys_kwargs = scales.keys2kwargs(*keys)
                keys_kwargs["height"] = self.height(keys_kwargs["username"])
                new_keys = tuple(keys_kwargs[kn] for kn in scaled.user_scales.keynames)
                scaled.user_scales[new_keys] = value
        else: # Updates common_scales and user_scales when needed
            for keys, value in scales:
                keys_kwargs = scales.keys2kwargs(*keys)
                keys_kwargs["height"] = self.default_height()
                new_keys = tuple(keys_kwargs[kn] for kn in scaled.common_scales.keynames)
                scaled.common_scales[new_keys] = value
            for username, model_cls in self.user_composition.items():
                for keys, value in scales:
                    keys_kwargs = scales.keys2kwargs(*keys)
                    keys_kwargs["username"] = username
                    keys_kwargs["height"] = self.height(username)
                    new_keys = tuple(keys_kwargs[kn] for kn in scaled.user_scales.keynames)
                    scaled.user_scales[new_keys] = value
        
        for username, composition in self.user_composition.items():
            scaled.user_compositions[username] = composition + [("scale", dict(note=note))]
        
        scaled._cache_users = dict()
        for username, model in self:
            scaled._cache_users[username] = ScoringModel(
                scaled.get_composition(username),
                model.directs,
                scaled.user_scales[username] | scaled.common_scales,
            )

        return scaled
    
    def squash(self, score_max: float, note: str="squash", **kwargs) -> "UserModels":
        new_composition = ("squash", dict(score_max=score_max, note=note))
        default_composition = self.default_composition + [new_composition]
        squashed = UserModels(self.user_directs, self.user_scales, self.common_scales, default_composition)
        for username, composition in self.user_composition.items():
            squashed.user_compositions[username] = composition + [new_composition]
        squashed._cache_users = dict()
        for username, model in self:
            composition = squashed.get_composition(username)
            squashed._cache_users[username] = ScoringModel(composition, model.directs, model.scales)
        return squashed
    
    @classmethod
    def load(cls, directory: str, **kwargs) -> "UserModels":
        for name, keynames in cls.table_keynames.items():
            if name in kwargs and isinstance(kwargs[name], str):
                df = pd.read_csv(f"{directory}/{kwargs[name]}", keep_default_na=False)
                kwargs[name] = MultiScore(keynames, df, name=name)
        return cls(**kwargs)
    
    def save(self, directory: Optional[str]=None, json_dump: bool=False) -> tuple[str, dict]:
        for table_name in self.table_keynames:
            filename = self.save_table(directory, table_name)
        return self.save_instructions(directory, json_dump)
    
    def save_instructions(self, directory: Optional[str]=None, json_dump: bool=False) -> tuple[str, dict]:
        kwargs = { name: f"{name}.csv" for name in self.table_keynames if getattr(self, name) }
        kwargs["default_composition"] = self.default_composition
        if len(self.user_composition) > 0:
            kwargs["user_composition"] = self.user_composition
        if directory is not None and json_dump:
            with open(Path(directory) / "user_models.json", "w") as f:
                json.dump([type(self).__name__, kwargs], f)
        return type(self).__name__, kwargs
        return cls(**kwargs)
    
    def save_table(self, directory: Union[Path, str], table_name: str) -> str:
        if getattr(self, table_name):
            getattr(self, table_name).save(directory, f"{table_name}.csv")
            return f"{table_name}.csv"
        return None
    
    def save_base_models(self, directory: Optional[str]=None) -> str:
        return self.save_table(directory, "user_directs")
    
    def save_user_scales(self, directory: Optional[str]=None) -> str:
        return self.save_table(directory, "user_scales")
    
    def save_common_scales(self, directory: Optional[str]=None) -> str:
        return self.save_table(directory, "common_scales")

    def __repr__(self) -> str:
        r = type(self).__name__ + ": " + " < ".join([o for o, _ in self.default_composition])
        return r + "\n\n" + "\n\n".join([
            f"{table_name}\n{repr(getattr(self, table_name))}" 
            for table_name in self.table_keynames
        ])
        
