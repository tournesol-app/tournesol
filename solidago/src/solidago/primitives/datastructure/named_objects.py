""" Rewrite Objects using pandas for speedup """

from abc import abstractmethod
from copy import deepcopy
from typing import Any, Generic, Hashable, Iterable, Iterator, Self, TypeVar
from pathlib import Path
from numpy.typing import NDArray

import numpy as np
import pandas as pd
import yaml

Object = TypeVar("Object")


class Contains:
    def __init__(self, value: str | Iterable[str]):
        self.value = value if isinstance(value, str) else set(value)

    def __call__(self, t: Iterable) -> bool:
        assert isinstance(t, Iterable)
        if isinstance(self.value, str):
            return self.value in t
        return bool(self.value & set(t))

    def __repr__(self) -> str:
        return f"Contains({self.value})"


class After:
    def __init__(self, value: int | float):
        self.value = value

    def __call__(self, t: int | float) -> bool:
        return t >= self.value

    def __repr__(self) -> str:
        return f"After({self.value})"


class NamedObject:
    default: dict[str, Any] = dict(trust=0.0)

    def __init__(self, name: str, series: pd.Series | None = None, vector: Iterable[float] | None = None, **kwargs):
        if series is None:
            self.series = pd.Series(kwargs, name=name)
        else:
            self.series = series
            self.series.name = name
            for key, value in kwargs.items():
                self.series[key] = value
        if vector is not None:
            for coordinate, value in enumerate(vector):
                self.series[f"v{coordinate}"] = value # type: ignore
        self._get_vector_coordinates()

    def _get_vector_coordinates(self):
        self._vector_coordinates, coordinate = list(), 0
        while f"v{coordinate}" in self.series:
            self._vector_coordinates.append(f"v{coordinate}")
            coordinate += 1
    
    @property
    def name(self) -> str:
        return str(self.series.name)

    @property
    def vector(self) -> NDArray[np.float64]:
        return self.series[self._vector_coordinates].astype(np.float64).to_numpy()
    
    def __contains__(self, key: str) -> bool:
        return (key in self.series) | (key in self.default)

    def __getitem__(self, key: str) -> Any:
        if key in self.series:
            return self.series[key]
        if key in self.default:
            return self.default[key]
        raise KeyError(key)

    def __setitem__(self, key: str, value: Any):
        self.series[key] = value
    
    def __repr__(self) -> str:
        return repr(self.series)


class NamedObjects(Generic[Object]):
    name: str = "objects"
    
    def __init__(self, 
        *args: Any, # df, name_list or pd.DataFrame args
        _name2index: pd.Series | None = None, 
        _index2name: list[str] | None = None, 
        **kwargs: Any
    ):
        if args and isinstance(args[0], pd.DataFrame):
            self.df = args[0]
        elif args and isinstance(args[0], list) and all(isinstance(n, str) for n in args[0]):
            self.df = pd.DataFrame(dict(name=args[0]))
        else:
            self.df = pd.DataFrame(*args, **kwargs)
        if not self.df.index.name == "name":
            if "name" in self.df.columns:
                self.df = self.df.set_index("name")
            self.df.index.name = "name"
        self._name2index, self._index2name = _name2index, _index2name
        self._get_vector_coordinates()

    @abstractmethod
    def row2object(self, row: pd.Series) -> Object:
        """ Transforms row series into a usable value for applications """

    def _get_vector_coordinates(self):
        self._vector_coordinates, coordinate = list(), 0
        while f"v{coordinate}" in self.df.columns:
            self._vector_coordinates.append(f"v{coordinate}")
            coordinate += 1

    def __len__(self) -> int:
        return len(self.df)

    def __bool__(self) -> bool:
        return len(self) > 0
    
    def __contains__(self, name: str | Object) -> bool:
        name = name if isinstance(name, str) else str(name.name) # type: ignore
        return name in self.names()

    def _cache_name2index(self):
        if self._name2index is not None and self._index2name is not None:
            return
        name2index, index2name = dict(), list()
        for index, (name, _) in enumerate(self.df.iterrows()):
            name2index[name] = np.int64(index)
            index2name.append(name)
        self._name2index = pd.Series(name2index, dtype=np.int64)
        self._index2name = index2name

    @property
    def vectors(self) -> NDArray[np.float64]:
        return self.df[self._vector_coordinates].astype(np.float64).to_numpy()
    
    def name2index(self, name: str | pd.Series | Object) -> np.int64:
        if not isinstance(name, str):
            assert hasattr(name, "name")
            name = str(name.name) # type: ignore - previous line guaranteed hasattr name
        self._cache_name2index()
        return self._name2index[name] # type: ignore - previous line guaranteed self._name2index is not None
        
    def index2name(self, index: int | np.int64) -> str:
        assert isinstance(index, (int, np.integer)), index
        assert index < len(self), index
        self._cache_name2index()
        return self._index2name[index] # type: ignore - previous line guaranteed self._index2name is not None
    
    def names(self) -> pd.Index:
        return self.df.index
    
    def __getitem__(self, name: int | np.integer | Hashable | Object) -> Object:
        if isinstance(name, (int, np.integer)):
            return self.row2object(self.df.iloc[name])
        elif hasattr(name, "name"):
            name = getattr(name, "name")
        rows = self.df.loc[str(name)]
        assert isinstance(rows, pd.Series)
        return self.row2object(rows)

    def filters(self, 
        names: Iterable[str | Hashable] | NDArray[np.int64] | pd.Index | None = None,
        **kwargs: str | tuple | Iterable | Hashable | Contains | After
    ) -> Self:
        if names is not None:
            names = names if isinstance(names, pd.Index) else list(names)
            return type(self)(self.df.loc[names]).filters(None, **kwargs)
        if not kwargs:
            return self
        key, value = next(iter(kwargs.items()))
        del kwargs[key]
        if isinstance(value, (str, tuple)):
            return type(self)(self.df[self.df[key] == value]).filters(None, **kwargs)
        if isinstance(value, (Contains, After)):
            return type(self)(self.df[self.df[key].map(value)]).filters(None, **kwargs)
        if isinstance(value, Iterable):
            return type(self)(self.df[self.df[key].isin(value)]).filters(None, **kwargs)
        return type(self)(self.df[self.df[key] == value]).filters(None, **kwargs)
    
    def excludes(self,
        names: Iterable[str | Hashable] | NDArray[np.int64] | pd.Index | None = None,
        **kwargs: str | tuple | Iterable | Hashable | Contains | After
    ) -> Self:
        if names is not None:
            remaining_names = [n for n in self.names() if n not in names]
            return type(self)(self.df.loc[remaining_names]).excludes(None, **kwargs)
        if not kwargs:
            return self
        key, value = next(iter(kwargs.items()))
        del kwargs[key]
        if isinstance(value, (str, tuple)):
            return type(self)(self.df[self.df[key] != value]).filters(None, **kwargs)
        if isinstance(value, (Contains, After)):
            return type(self)(self.df[~self.df[key].map(value)]).filters(None, **kwargs)
        if isinstance(value, Iterable):
            return type(self)(self.df[~self.df[key].isin(value)]).filters(None, **kwargs)
        return type(self)(self.df[self.df[key] == value]).filters(None, **kwargs)

    def __setitem__(self, key: tuple[str, str], value: Any):
        self.df.loc[key[0], key[1]] = value
    
    def sample(self, n_items: int | None = None) -> Self:
        """ If n_items is None, returns deepcopy """
        if n_items is None or len(self) < n_items:
            return deepcopy(self)
        indices = np.random.choice(len(self), n_items, False)
        return type(self)(self.df.iloc[indices])
    
    def append(self, object: Object | pd.Series):
        row = object if isinstance(object, pd.Series) else object.to_row() # type: ignore
        assert hasattr(object, "name"), object
        self.append_row(str(object.name), row) # type: ignore
    
    def append_row(self, name: str, row: pd.Series):
        self.df.loc[name] = row
        if self._name2index is not None:
            assert self._index2name is not None
            self._name2index[name] = len(self) - 1
            self._index2name.append(name)
    
    def __or__(self, other: Self) -> Self:
        return type(self)(pd.concat([self.df, other.df]))

    def set_column(self, name: str, column: pd.Series | list | NDArray):
        self.df[name] = column
        if name.startswith("v") and name[1:].isdigit():
            self._get_vector_coordinates()

    def assign(self, **kwargs: Any) -> Self:
        df = self.df.assign(**kwargs)
        return type(self)(df, _name2index=deepcopy(self._name2index), _index2name=deepcopy(self._index2name))

    def __iter__(self) -> Iterator[Object]:
        for _, row in self.df.iterrows():
            yield self.row2object(row)
    
    def iter_pairs(self, shuffle: bool = False) -> Iterator[tuple[Object, Object]]:
        for i in range(len(self)):
            for j in range(i):
                s = shuffle and np.random.random() < 0.5
                pair = (self[i], self[j]) if s else (self[j], self[i])
                yield pair # type: ignore - Cannot be Self given i, j are int

    def get_column(self, name: str) -> pd.Series:
        return self.df[name]
    
    def get_columns(self, names: Iterable[str]) -> pd.DataFrame:
        return self.df[list(names)]

    def drop(self, names: Iterable[str] | str) -> Self:
        names = [names] if isinstance(names, str) else list(names)
        return type(self)(self.df.drop(names))
    
    def shuffle(self, shuffle: bool = True) -> Self:
        if not shuffle:
            return self
        return type(self)(self.df.sample(frac=1))

    def sort_by(self, column: str, ascending: bool = True) -> Self:
        return type(self)(self.df.sort_values(by=column, ascending=ascending))
    
    def tail(self, n_rows: int) -> Self:
        return type(self)(self.df.tail(n_rows))
    
    def head(self, n_rows: int) -> Self:
        return type(self)(self.df.head(n_rows))

    @classmethod
    def load(cls, directory: str | Path, source: str | None = None, **kwargs: Any) -> Self:
        directory = Path(directory)
        if directory.is_file():
            path = Path(directory)
            source = path.name
        else:
            source = source or cls.name
            if (directory / source).is_file():
                pass
            elif (directory / f"{source}.parquet").is_file():
                source = f"{source}.parquet"
            elif (directory / f"{source}.csv").is_file():
                source = f"{source}.csv"
            path = Path(directory) / source
        source = source or cls.name
        if not path.is_file():
            return cls(**kwargs)
        if source.endswith(".parquet"):
            df = pd.read_parquet(path)
        else:
            assert source.endswith(".csv")
            df = pd.read_csv(path)
        return cls(df, **kwargs)

    def save(self, 
        directory: str | Path | None = None, 
        source: str | None = None, 
        save_instructions: bool = False, # not used
    ) -> tuple[str, dict]:
        source = source or f"{self.name}.parquet"
        if not directory:
            return self.save_instructions(source, directory, save_instructions)
        path = f"{directory}/{source}"
        if source.endswith(".parquet"):
            self.df.to_parquet(path)
        elif source.endswith(".csv"):
            self.df.to_csv(path)
        return self.save_instructions(source, directory, save_instructions)

    def save_instructions(self, 
        source: str | None = None, 
        directory: str | Path | None = None, 
        save_instructions: bool=True,
    ) -> tuple[str, dict[str, Any]]:
        source = source or f"{self.name}.parquet"
        kwargs = dict(source=source)
        instructions = type(self).__name__, kwargs
        if directory and save_instructions:
            filename = (".".join(source.split(".")[:-1]) + ".yaml") if "." in source else f"{source}.yaml"
            with open(Path(directory) / filename, "w") as f:
                yaml.safe_dump(instructions, f)
        return instructions
    
    def requires_save_instructions(self) -> bool:
        return False # default value

    def __repr__(self) -> str:
        return repr(self.df)
    

class SeriesNamedObjects(NamedObjects[pd.Series]):
    def row2object(self, row: pd.Series) -> pd.Series:
        return row