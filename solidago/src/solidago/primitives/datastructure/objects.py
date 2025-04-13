from typing import Union, Optional, Iterable, Any
from pathlib import Path

import numpy as np
import pandas as pd


class Object:
    def __init__(self, name: Union[str, int], vector: list=[], **kwargs):
        assert isinstance(name, (str, int))
        self.name = name
        self.vector = np.array(vector, dtype=np.float64)
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
    
    def to_dict(self) -> dict:
        kwargs = {key: value for key, value in self.__dict__.items()}
        del kwargs["vector"]
        for i in range(len(self.vector)):
            kwargs[f"vector_{i}"] = self.vector[i]
        return kwargs
    
    def deepcopy(self) -> "Object":
        return type(self)(**self.__dict__)
    
    def __repr__(self) -> str:
        return f"{type(self).__name__} {self.name}\n" + "\n".join([
            f"{key} = {value}" for key, value in self.__dict__.items()
            if key not in {"name", "vector"}
        ])
        

class Objects:
    name: str="objects"
    index_name: str="name"
    object_cls: type=Object
    
    def __init__(self, init_data: Optional[Union[pd.DataFrame, dict, Iterable]]=None):
        self.init_data = init_data
        self._dict, self._name2index, self._index2name = dict(), None, None
    
    def _cache(self) -> None:
        if isinstance(self.init_data, dict):
            self._name2index, self._index2name = None, None
            for index, (name, obj) in enumerate(self.init_data.items()):
                self._dict[name] = type(self).object_cls.load(name)
                self._name2index[name] = index
                self._index2name[index] = name
        elif isinstance(self.init_data, pd.DataFrame):
            self._name2index, self._index2name = None, None
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
    
    def name2index(self, name: Union[int, str, Object]) -> int:
        self._cache_name2index()
        name = name.name if isinstance(name, Object) else name
        return self._name2index[name]
        
    def index2name(self, index: int) -> Union[int, str]:
        self._cache_name2index()
        return self._index2name[index]
        
    def get_by_index(self, index: int) -> Union[int, str]:
        return self[self.index2name(index)]
    
    def __getitem__(self, name: Union[int, str, Object, Iterable]) -> Object:
        if isinstance(name, type(self).object_cls):
            assert name in self
            return name
        self._cache()
        if isinstance(name, (str, int)):
            return self._dict[name]
        return type(self)([obj for obj in name])
    
    def __delitem__(self, obj: Union[int, str, Object, Iterable]) -> Object:
        self._cache()
        if isinstance(obj, type(self).object_cls):
            del obj.name
        if isinstance(name, (str, int)):
            return self._dict[name]
    
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
        self._index2name[len(self._dict)] = obj.name
    
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

    def to_df(self, n_max: Optional[int]=None) -> pd.DataFrame:
        self._cache()
        data = dict()
        for index, obj in enumerate(self):
            if index > n_max:
                break
            data[obj.name] = obj.to_dict()
        return pd.DataFrame(data).T

    @classmethod
    def load(cls, directory: str, name: Optional[str]=None):
        name = name or cls.name
        try:
            df = pd.read_csv(f"{directory}/{name}.csv", keep_default_na=False)
            return cls(df)
        except:
            return cls()

    def save(self, directory: Optional[str]=None, name: Optional[str]=None) -> tuple[str, dict]:
        name = name or type(self).name
        if directory is not None:
            self.to_df().to_csv(Path(directory) / f"{name}.csv")
        return self.save_instructions()

    def save_instructions(self, name: Optional[str]=None) -> tuple[str, dict]:
        name = name or type(self).name
        return type(self).__name__, dict(name=name)

    def __len__(self) -> int:
        if self.init_data is not None:
            return len(self.init_data)
        return len(self._dict)

    def __contains__(self, obj: Union[str, int, Object]) -> bool:
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
    
