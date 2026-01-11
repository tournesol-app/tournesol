from typing import Iterable, Any, Union
from pathlib import Path

import numpy as np
import pandas as pd
import random


class Object:
    def __init__(self, name: str | int, vector: list | None = None, **kwargs):
        assert isinstance(name, (str, int))
        self.name = name
        self.vector = np.array(list() if vector is None else vector, dtype=np.float64)
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def load(cls, data: Union["Object", int, str, dict, Iterable]) -> "Object":
        if isinstance(data, cls):
            return data
        elif isinstance(data, (int, str)):
            return cls(data)
        elif isinstance(data, dict):
            return cls(**data)
        elif isinstance(data, Iterable):
            return cls(*data)
        else:
            raise ValueError(f"Object {data} of type {type(data)} not handled")
    
    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)
    
    def __setitem__(self, key: str, value: Any) -> None:
        setattr(self, key, value)

    def __contains__(self, key: str) -> bool:
        return hasattr(self, key)
    
    def to_dict(self) -> dict:
        kwargs = {key: value for key, value in self.__dict__.items()}
        del kwargs["vector"]
        for i in range(len(self.vector)):
            kwargs[f"vector_{i}"] = self.vector[i]
        return kwargs
    
    def deepcopy(self) -> "Object":
        return type(self)(**self.__dict__)
    
    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return f"{type(self).__name__} {self.name}\n" + "\n".join([
            f"{key} = {value}" for key, value in self.__dict__.items()
            if key not in {"name", "vector"}
        ])
        

class Objects:
    name: str="objects"
    index_name: str="name"
    object_cls: type=Object
    
    def __init__(self, init_data: pd.DataFrame | dict | Iterable | None = None):
        self.init_data = init_data
        self._dict, self._name2index, self._index2name = dict(), None, None
    
    def _cache(self) -> None:
        if isinstance(self.init_data, dict):
            self._name2index, self._index2name = None, None
            for index, (name, obj) in enumerate(self.init_data.items()):
                self._dict[name] = type(self).object_cls.load(name)
        elif isinstance(self.init_data, pd.DataFrame):
            self._name2index, self._index2name = None, None
            if type(self).index_name in self.init_data.columns:
                self.init_data = self.init_data.set_index(type(self).index_name)
            vector_dim, vector_columns = 0, list()
            while f"vector_{vector_dim}" in self.init_data.columns:
                vector_columns.append(f"vector_{vector_dim}")
                vector_dim += 1
            for index, (name, row) in enumerate(self.init_data.iterrows()):
                vector = row[vector_columns].to_numpy(dtype=np.float64)
                kwargs = dict(row)
                if "name" not in kwargs:
                    kwargs["name"] = name
                for vector_column in vector_columns:
                    del kwargs[vector_column]
                self._dict[kwargs["name"]] = type(self).object_cls(vector=vector, **kwargs)
        elif isinstance(self.init_data, Iterable):
            self._name2index, self._index2name = None, None
            for index, data in enumerate(self.init_data):
                obj = type(self).object_cls.load(data)
                self._dict[obj.name] = obj
        self.init_data = None
        self._cache_name2index()
    
    def _cache_name2index(self) -> None:
        if self._name2index is not None and self._index2name is not None:
            return None
        self._name2index, self._index2name = dict(), list()
        for index, obj in enumerate(self):
            self._name2index[obj.name] = index
            self._index2name.append(obj.name)
    
    @property
    def vectors(self) -> np.ndarray:
        self._cache()
        return np.array([obj.vector for obj in self])
    
    def name2index(self, name: int | str | Object) -> int:
        self._cache_name2index()
        name = name.name if isinstance(name, Object) else name
        return self._name2index[name]
        
    def index2name(self, index: int) -> int | str:
        self._cache_name2index()
        assert isinstance(index, (int, np.int64, np.int32)), index
        assert index < len(self), index
        return self._index2name[index]
        
    def get_by_index(self, index: int) -> Object:
        return self[self.index2name(index)]
    
    def __getitem__(self, name: int | str | Object | Iterable) -> Object:
        if isinstance(name, type(self).object_cls):
            assert name in self
            return name
        self._cache()
        if isinstance(name, (str, int)):
            return self._dict[name]
        return type(self)([obj for obj in name])
    
    def sample(self, n_items: int | None = None) -> "Objects":
        if n_items is None or len(self) < n_items:
            return self.deepcopy()
        return self[random.sample(self.keys(), n_items)]
    
    def __delitem__(self, obj: int | str | Object | Iterable) -> Object:
        self._cache()
        if isinstance(obj, type(self).object_cls):
            del self._dict[obj.name]
        elif isinstance(obj, (str, int)):
            del self._dict[obj]
        else:
            assert isinstance(obj, Iterable)
            for o in obj:
                del self[o]
    
    def keys(self) -> list:
        return [obj.name for obj in self]
    
    def values(self, key: str) -> list:
        return [obj[key] for obj in self]
    
    def add(self, obj: Object) -> None:
        assert isinstance(obj, type(self).object_cls)
        assert obj.name not in self
        self._cache()
        self._dict[obj.name] = obj
        self._name2index[obj.name] = len(self._dict)
        self._index2name.append(obj.name)
    
    def deepcopy(self) -> "Objects":
        return type(self)([obj.deepcopy() for obj in self])
    
    def assign(self, **kwargs) -> "Objects":
        result = self.deepcopy()
        for key, value in kwargs.items():
            try:
                assert len(value) == len(self)
                if isinstance(value, dict):
                    for index, obj in enumerate(result):
                        setattr(obj, key, value[obj.name])
                else:
                    for index, obj in enumerate(result):
                        setattr(obj, key, value[index])
            except (TypeError, AssertionError, KeyError):
                for index, obj in enumerate(result):
                    setattr(obj, key, value)
        return result

    def __iter__(self) -> Iterable:
        self._cache()
        for obj in self._dict.values():
            yield obj
    
    def iter_pairs(self, shuffle: bool = False) -> Iterable:
        self._cache()
        objects = list(self._dict.values())
        for i in range(len(objects)):
            for j in range(i):
                s = shuffle and np.random.random() < 0.5
                pair = (objects[i], objects[j]) if s else (objects[j], objects[i])
                yield pair

    def to_df(self, n_max: int | None = None) -> pd.DataFrame:
        self._cache()
        data = dict()
        for index, obj in enumerate(self):
            if n_max is not None and index > n_max:
                break
            data[obj.name] = obj.to_dict()
        index_name = type(self).index_name
        return pd.DataFrame(data).T.rename(columns={"name": index_name}).set_index(index_name)

    @classmethod
    def load(cls, directory: str, source: str | None = None):
        source = source or cls.name
        try:
            df = pd.read_csv(f"{directory}/{source}.csv", keep_default_na=False)
            return cls(df)
        except:
            return cls()

    def save(self, directory: str | None = None, source: str | None = None) -> tuple[str, dict]:
        source = source or type(self).name
        if directory is not None:
            self.to_df().to_csv(Path(directory) / f"{source}.csv")
        return self.save_instructions(source)

    def save_instructions(self, source: str | None = None) -> tuple[str, dict]:
        kwargs = dict()
        if source is not None and source != self.name:
            kwargs["source"] = source
        return type(self).__name__, kwargs

    def __len__(self) -> int:
        if self.init_data is not None:
            return len(self.init_data)
        return len(self._dict)

    def __contains__(self, obj: str | int | Object) -> bool:
        self._cache()
        name = obj.name if isinstance(obj, type(self).object_cls) else obj
        return name in self._dict

    def __bool__(self) -> bool:
        return len(self) > 0

    def __repr__(self, n_displayed: int=8) -> str:
        if self.init_data is not None:
            return f"{type(self).__name__} (not cached yet):\n{repr(self.init_data)}"
        result = f"{type(self).__name__}\n{repr(self.to_df(n_displayed))}"
        length = len(self)
        return result + (f"\n... ({length} items)" if length > 8 else "")
    
