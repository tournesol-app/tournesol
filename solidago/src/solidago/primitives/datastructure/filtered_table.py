from collections.abc import Mapping, Sequence
from copy import deepcopy
from pathlib import Path
from typing import Any, Hashable, Iterable, Iterator, Literal, Generic, Optional, TypeVar, Self, Union
from numpy.typing import NDArray, DTypeLike

import numpy as np
import pandas as pd
import yaml


Scalar = Hashable | float | np.float32 | np.float64 | None
TableRow = TypeVar('TableRow')
Select = Literal["unique", "first", "last", "default"]


class Row:
    default: dict[str, Any] = dict()

    def __init__(self, series: pd.Series | None = None, _table: Optional["_Table"] = None, **kwargs: Any):
        self.series = pd.Series() if series is None else series
        assert isinstance(self.series, pd.Series), self.series
        self._table = _table
        for key, value in kwargs.items():
            self[key] = value
        for key, value in self.default.items():
            if key not in self.series:
                self[key] = value

    def __contains__(self, key: str) -> Any:
        return key in self.series

    def __getitem__(self, key: str) -> Any:
        return self.series[key]

    def __setitem__(self, key: str, value: Any):
        if self._table is not None:
            name = self.series.name
            assert isinstance(name, (str, int, np.integer)), name
            self._table.df.loc[name, key] = value
        else:
            self.series[key] = value
    
    def __repr__(self) -> str:
        return repr(self.series)

    def __eq__(self, other: object) -> bool:
        assert isinstance(other, Row)
        return dict(self.series) == dict(other.series)

    def __deepcopy__(self, memo) -> Self:
        return type(self)(series=deepcopy(self.series))

    def keys(self, *keynames: str) -> dict[str, Hashable]:
        return {name: self[name] for name in keynames}
    
    def to_dict(self) -> dict[str, Any]:
        return dict(self.series)

    def detach(self):
        self._table = None
        self.series = pd.Series(self.to_dict())


class NonUniqueError(Exception):
    pass


class Filter:
    def __init__(self, indices: NDArray[np.int64] | None = None, **keys: Hashable):
        self.indices = indices
        self.keys = keys
    
    def __bool__(self) -> bool:
        return self.indices is not None

    def __and__(self, other: "Filter") -> "Filter":
        assert all(self.keys[name] == other.keys[name] for name in set(self.keys) & set(other.keys))
        if self.indices is None and other.indices is None:
            return Filter(None, **self.keys | other.keys)
        if self.indices is None:
            assert other.indices is not None
            indices = deepcopy(other.indices)
        elif other.indices is None:
            assert self.indices is not None
            indices = deepcopy(self.indices)
        else:
            indices = np.intersect1d(self.indices, other.indices)
        return Filter(indices, **self.keys | other.keys)

    def __or__(self, other: "Filter", self_len: int, other_len: int) -> "Filter":
        assert all(self.keys[name] == other.keys[name] for name in set(self.keys) & set(other.keys)), \
            (self.keys, other.keys)
        keys = self.keys | other.keys
        self_indices = np.arange(self_len) if self.indices is None else self.indices
        other_indices = np.arange(other_len) if other.indices is None else other.indices
        indices = np.append(self_indices, other_indices + self_len).astype(np.int64)
        return Filter(indices, **keys)
    
    def remove_index(self, index: np.int64):
        if self.indices is None:
            return
        index_in_indices = np.where(self.indices == index)[0]
        assert len(index_in_indices) == 1
        self.indices = np.delete(self.indices, index_in_indices[0]).astype(np.int64)
    
    def add_index(self, index: np.int64):
        if self.indices is None:
            return
        assert self.indices is not None
        self.indices = np.append(self.indices, index).astype(np.int64)

    def get_indices(self, n_rows: int | np.int64) -> NDArray[np.int64]:
        return np.arange(n_rows, dtype=np.int64) if self.indices is None else self.indices
    
    def get_index(self, select: Literal["first", "last", "unique"] = "unique") -> np.int64 | None:
        if self.indices is None:
            return np.int64(-1 if select == "last" else 0)
        if len(self.indices) == 0:
            return None
        if select == "unique" and len(self.indices) > 1:
            raise NonUniqueError
        return max(self.indices) if select == "last" else min(self.indices)

    def must_be_filtered_in(self, row: pd.Series | Mapping[str, Scalar]) -> bool:
        return all(row[name] == key for name, key in self.keys.items())
    
    def must_be_filtered_out(self, row: pd.Series | Mapping[str, Scalar]) -> bool:
        return not self.must_be_filtered_in(row)
    
    def __repr__(self) -> str:
        if not self:
            return "No filter"
        return f"Filters " + ', '.join(f'{n}={k}' for n, k in self.keys.items()) + f", indices={self.indices}"


class _TableCache:
    def __init__(self, indices: dict[str, dict[Hashable, pd.Index | NDArray[np.int_] | list[int]]] | None = None):
        self._indices = indices or dict() # indices[keyname, key] = {indices}

    def cache(self, keyname: str, table: "_Table", force: bool=False):
        if keyname in self._indices and not force:
            return
        assert keyname in table.df.columns, (keyname, table.df.columns)
        self._indices[keyname] = table.df.groupby(keyname).indices
    
    def keynames(self) -> set[str]:
        return set(self._indices.keys())
    
    def keys(self, keyname: str) -> set[Hashable]:
        return set(self._indices[keyname].keys())
    
    def add(self, index: int | np.int64, keyname: str, key: Hashable):
        assert keyname in self._indices
        self._indices[keyname][key] = np.append(self.indices(keyname, key), index)

    def remove(self, index: int | np.int64, keyname: str, key: Hashable):
        # does not remove key from self.keys[keyname]
        indices = self.indices(keyname, key)
        indices_in_indices = np.where(indices == index)[0]
        assert len(indices_in_indices) == 1, (indices, index)
        self._indices[keyname][key] = np.delete(indices, indices_in_indices[0])

    def indices(self, keyname: str, key: Hashable) -> NDArray[np.int64]:
        try:
            indices = self._indices[keyname][key]
            if isinstance(indices, pd.Index):
                return indices.to_numpy()
            elif isinstance(indices, list):
                return np.array(indices)
            return indices
        except KeyError:
            return np.array([], dtype=np.int64)

    def shift(self, shift: int | np.int64) -> "_TableCache":
        return _TableCache({
            keyname: {
                key: self.indices(keyname, key) + shift
                for key in self.keys(keyname)
            } for keyname in self.keynames()
        })

    def __or__(self, other: Self) -> "_TableCache":
        assert self.keynames() == other.keynames()
        return _TableCache({
            keyname: {
                key: np.append(self.indices(keyname, key), other.indices(keyname, key)).astype(np.int64)
                for key in self.keys(keyname) | other.keys(keyname)
            } for keyname in self.keynames() | other.keynames()
        })
    
    def __repr__(self) -> str:
        if not self.keys:
            return "No cache"
        r = ""
        for keyname in self.keynames():
            for key in self.keys(keyname):
                r += f"Cached {keyname}, {key}: {set(self.indices(keyname, key))}\n"
        return r


class _Table:
    def __init__(self, df: pd.DataFrame, _cache: _TableCache | None = None, version: int = 0):
        assert isinstance(df, pd.DataFrame), (df, type(df))
        assert _cache is None or isinstance(_cache, _TableCache), _cache
        assert isinstance(version, int), version
        self.df = df
        self.version = version
        self._cache = _cache or _TableCache()
    
    def __len__(self) -> int:
        return len(self.df)

    def cache(self, *keynames: str):
        for keyname in keynames:
            self._cache.cache(keyname, self)
    
    def keys(self, keyname: str) -> set[Hashable]:
        self.cache(keyname)
        return self._cache.keys(keyname)
    
    def indices(self, keyname: str, key: Hashable) -> NDArray[np.int64]:
        self.cache(keyname)
        return self._cache.indices(keyname, key)

    def get_filter(self, **keys: Hashable | list[Hashable]) -> Filter:
        """ Filtered tables only have a changed filter """
        assert all(name in self.df.columns for name in keys), (keys, self.df.columns)
        self.cache(*keys.keys())
        filter = Filter()
        for name, key in keys.items():
            if isinstance(key, list):
                indices = np.concatenate([self._cache.indices(name, k) for k in key], dtype=np.int64)
                filter = filter & Filter(indices)
            else:
                indices = self._cache.indices(name, key)
                filter = filter & Filter(indices, **{name: key})
        return filter
    
    def __or__(self, other: Self) -> "_Table":
        """ Filtered table points to the same column names and dtypes as self """
        if len(self.df) == 0:
            return other
        elif len(other.df) == 0:
            return self
        assert set(other.df.columns) == set(self.df.columns), (other.df.columns, self.df.columns)
        other_df = deepcopy(other.df)
        other_shift = len(self.df)
        other_df.index = other_df.index + other_shift
        df = pd.concat([self.df, other.df], ignore_index=True)
        self.cache(*other._cache.keynames())
        other.cache(*self._cache.keynames())
        other_cache = other._cache.shift(other_shift)
        return _Table(df, self._cache | other_cache)

    def set(self, index: int | np.int64, column_name: str, value: Any):
        removed_value = self.df.loc[int(index), column_name]
        if column_name in self._cache.keynames():
            assert isinstance(removed_value, Hashable), (removed_value, type(removed_value))
            self._cache.remove(index, column_name, removed_value)
        self.df.loc[int(index), column_name] = value
        if column_name in self._cache.keynames():
            assert isinstance(value, Hashable), (value, type(value))
            self._cache.add(index, column_name, value)
        
    def set_row(self, index: int | np.int64, row: pd.Series | Mapping[str, Scalar]):
        removed_row = self.df.loc[index]
        for keyname in self._cache.keynames():
            key = removed_row[keyname]
            assert isinstance(key, Hashable), (key, type(key))
            self._cache.remove(index, keyname, key)
        self.df.loc[int(index)] = pd.Series(row)
        for keyname in self._cache.keynames():
            key = row[keyname]
            self._cache.add(index, keyname, key)
        self.version += 1

    def append_row(self, row: pd.Series | Mapping[str, Scalar]):
        index = len(self.df)
        self.df.loc[index] = dict(row) # type: ignore
        for keyname in self._cache.keynames():
            key = row[keyname]
            self._cache.keys(keyname).add(key)
            self._cache.add(np.int64(index), keyname, key)
        self.version += 1

    def set_column(self, 
        column_name: str, 
        values: Scalar | Sequence[Scalar] | NDArray[np.float64], 
        dtype: type | None = None,
    ):
        if dtype:
            self.df.dtypes[column_name] = dtype
        assert isinstance(column_name, str), column_name
        self.df[column_name] = values # type: ignore
        if column_name in self._cache.keynames():
            self._cache.cache(column_name, self, force=True)

    def set_columns(self, 
        dtypes: dict[str, type] | None = None, 
        **values: Scalar | Sequence[Scalar] | NDArray[np.float64]
    ):
        for name, value in values.items():
            dtype = dtypes[name] if dtypes and name in dtypes else None
            self.set_column(name, value, dtype)

    def add_columns(self, dtypes: dict[str, type] | None = None, **values: Scalar | Sequence[Scalar] | NDArray[np.float64]) -> Self:
        copy = deepcopy(self)
        copy.set_columns(dtypes, **values)
        return copy
    
    def repr_cache(self) -> str:
        return repr(self._cache)

    def __repr__(self) -> str:
        return f"{self._cache}\n\n{self.df}"
    

class FilteredTable(Generic[TableRow]):
    """ Datastructure for tables of entries without index column. 
    The extraction of all table entries that match some values for some columns must be made efficient, 
    as well as the iteration over the resulting subtable.
    The trick to do so is to maintain two caches that locate the indices of the rows
    that correspond to a column-index match, and use set operations on such indices. """

    #########################################################################################
    ##  The following attributes and methods could be worth redefining in derived classes  ##
    ## The default TableRow is dict, but could be specified differently in derived classes ##
    #########################################################################################

    TableRowType: type = Row
    name: str = "filtered_table"

    default_column_names: list[str] = list()
    default_keynames: set[str] = set()
    default_dtypes: dict[str, DTypeLike] = dict()
    default_select: Literal["unique", "first", "last"] = "unique"

    ########################################
    ## The following methods are standard ##
    ########################################

    def row_factory(self, **keys: Hashable) -> TableRow:
        return self.TableRowType(None, **keys)

    def series2row(self, series: pd.Series) -> TableRow:
        """ Transforms row as tuple into a usable row for applications """
        return self.TableRowType(series=series, _table=self.table)
    
    def _row2series(self, row: TableRow) -> pd.Series:
        """ Tries to convert row into a pandas Series. This may not be possible.
        Note that the returned tuple does not need to handle dtype.
        The method that is used is self.row2series, which involves dtype post-processing
        given the output of self._row2series """
        try:
            return row.series # type: ignore - Error caught
        except AttributeError:
            raise ValueError(f"Cannot transform row {row} of type {type(row).__name__} into series")
    
    def __init__(self, 
        *args: Any, 
        filter: Filter | None = None, 
        keynames: Iterable[str] | None = None, 
        **kwargs: Any,
    ):
        """ Either args is simply (table: _Table,) or (*args, **kwargs) are used to construct table """
        if args and isinstance(args[0], _Table):
            self.table = args[0]
        elif args and isinstance(args[0], pd.DataFrame):
            self.table = _Table(args[0])
        else:
            if "columns" not in kwargs:
                kwargs["columns"] = self.default_column_names
            self.table = _Table(pd.DataFrame(*args, **kwargs))
        self.table_version = self.table.version
        self.keynames = self.default_keynames if keynames is None else set(keynames)
        for keyname in self.keynames:
            if keyname not in self.columns:
                assert not self.table, (
                    f"Cannot add non-column keyname '{keyname}' at init. "
                    f"Columns are {self.columns}. "
                    f"Please add '{keyname}' to columns or modify keynames arg."
                )
                self.table.df[keyname] = ""
        assert filter is None or isinstance(filter, Filter)
        self._filter = filter or Filter() # self.filter handles version update

    def cache(self, *column_names: str):
        self.table.cache(*column_names)

    @property
    def columns(self) -> tuple[str, ...]:
        return tuple(self.table.df.columns)

    @property
    def n_columns(self) -> int:
        return len(self.table.df.columns)
    
    @property
    def filter(self) -> Filter:
        if not self._filter:
            return self._filter
        if self.table_version != self.table.version:
            assert self.table_version < self.table.version
            self._fitler = self.table.get_filter(**self._filter.keys)
            self.table_version = self.table.version
        return self._filter
    
    @property
    def indices(self) -> NDArray[np.int64]:
        if self.filter.indices is None:
            return np.arange(len(self), dtype=np.int64)
        return self.filter.indices

    @property
    def df(self) -> pd.DataFrame:
        if not self.filter:
            return self.table.df
        df = self.table.df.loc[self.filter.indices]
        assert isinstance(df, pd.DataFrame)
        df.index = list(range(len(df)))
        return df

    def _get_filter(self, **keys: Hashable | list[Hashable]) -> Filter:
        return self.filter & self.table.get_filter(**keys)
    
    def filters(self, **keys: Hashable | list[Hashable]) -> Self:
        keynames = [name for name in self.keynames if name not in keys or isinstance(keys[name], list)]
        return type(self)(self.table, filter=self._get_filter(**keys), keynames=keynames, **self.filters_kwargs())
    
    def filters_kwargs(self) -> dict[str, Any]:
        return dict()

    def iter_filters(self, *keynames: str) -> Iterator[tuple[tuple[Hashable, ...], Filter]]:
        if not keynames:
            yield (), self.filter
            return
        for key in self.table.keys(keynames[0]):
            indices = self.table.indices(keynames[0], key)
            for other_keys, subtable in self.iter(*keynames[1:]):
                assert isinstance(key, Hashable)
                assert isinstance(subtable, FilteredTable)
                filter = Filter(indices, **{keynames[0]: key}) & subtable.filter
                if filter.indices is None or len(filter.indices) > 0:
                    yield (key, *other_keys), filter

    def iter(self, 
        *keynames: str, 
        select: Select | None = None
    ) -> Iterator[tuple[tuple[Hashable, ...], Self | TableRow]]:
        for keys, filter in self.iter_filters(*keynames):
            table = type(self)(self.table, filter=filter)
            result = table if select is None else table.get(select)
            assert result is not None, result
            yield keys, result
    
    def iter_indices(self) -> Iterator[np.int64]:
        for index in self.filter.get_indices(len(self.table)):
            yield index

    def _iter_series(self) -> Iterator[pd.Series]:
        for index in self.filter.get_indices(len(self.table)):
            yield self._get_series(index)

    def __iter__(self) -> Iterator[TableRow]:
        for row in self._iter_series():
            yield self.series2row(row)

    def keys(self, keyname: str) -> set[Hashable]:
        if self.filter.indices is None:
            return self.table.keys(keyname)
        return set(self.table.df.loc[self.filter.indices, keyname])

    def multikeys(self, *keynames: str) -> set[tuple[Hashable, ...]]:
        return {tuple(row[name] for name in keynames) for row in self._iter_series()}

    def get_index(self, select: Select = "default", **keys: Hashable) -> np.int64 | None:
        if select == "default":
            select = self.default_select
        try:
            if not keys:
                return self.filter.get_index(select)
            return self._get_filter(**keys).get_index(select)
        except NonUniqueError:
            raise NonUniqueError(select, keys, self.filter.keys, self)

    def get(self, select: Select = "default", **keys: Hashable) -> TableRow:
        index = self.get_index(select, **keys)
        return self._get_row(index, **keys)
    
    def __getitem__(self, index: int | np.int64 | None) -> TableRow:
        return self._get_row(index)
    
    def _get_row(self, index: int | np.int64 | None, **keys: Hashable) -> TableRow:
        if index is None:
            return self.row_factory(**(keys | self.filter.keys))
        return self.series2row(self._get_series(index))

    def _get_series(self, index: int | np.int64) -> pd.Series:
        assert index in self.table.df.index, (index, self.table.df.index)
        row = self.table.df.loc[index]
        assert isinstance(row, pd.Series)
        return row

    def get_keys(self, row: TableRow, keynames: set[str] | None = None) -> dict[str, Hashable]:
        keynames = self.keynames if keynames is None else keynames
        return {name: row[name] for name in keynames} # type: ignore - TableRow must have __getitem__

    def row2series(self, row: TableRow | Mapping[str, Scalar] | Sequence[Scalar]) -> pd.Series:
        if isinstance(row, Sequence):
            d = dict(zip(self.columns, row))
            return pd.Series(d)
        if isinstance(row, Mapping):
            return pd.Series(row)
        return self._row2series(row)

    def _must_be_filtered_out(self, row: pd.Series | Mapping[str, Scalar]) -> bool:
        return self.filter.must_be_filtered_out(row)

    def __bool__(self) -> bool:
        return len(self.filter.indices) > 0 if self.filter.indices is not None else len(self.table.df) > 0

    def __len__(self) -> int:
        return len(self.filter.indices) if self.filter.indices is not None else len(self.table)

    def __or__(self, other: "FilteredTable") -> Self:
        return type(self)(
            self.table | other.table, 
            filter=self.filter.__or__(other.filter, len(self.table), len(other.table)), 
            keynames=self.keynames, 
            **self.filters_kwargs()
        )

    def get_column(self, column_name: str) -> pd.Series:
        if self.filter.indices is not None:
            series = self.table.df.loc[self.filter.indices][column_name]
        else:
            series = self.table.df[column_name]
        return series

    def set_columns(self, 
        dtypes: dict[str, type] | None = None, 
        **values: Scalar | Sequence[Scalar] | NDArray[np.float64]
    ):
        """ Modifies table. This does not affect filters. """
        if self.filter.indices is None:
            self.table.set_columns(dtypes, **values)
        else:
            for column, column_values in values.items():
                column_index = self.table.df.columns.get_loc(column)
                self.table.df.iloc[self.filter.indices, column_index] = column_values # type: ignore

    def add_columns(self, 
        dtypes: dict[str, type] | None = None, 
        **values: Scalar | Sequence[Scalar] | NDArray[np.float64]
    ) -> Self:
        return type(self)(
            self.table.add_columns(dtypes, **values), 
            keynames=self.keynames, 
            filter=deepcopy(self.filter), 
            **self.filters_kwargs()
        )
    
    def set_keys(self, 
        dtypes: dict[str, type] | None = None, 
        **values: Scalar | Sequence[Scalar] | NDArray[np.float64]
    ):
        """ Modifies table. This does not affect filters. """
        self.set_columns(dtypes, **values)
        self.keynames.update(values)

    def add_keys(self, 
        dtypes: dict[str, type] | None = None, 
        **values: Scalar | Sequence[Scalar] | NDArray[np.float64]
    ) -> Self:
        result = self.add_columns(dtypes, **values)
        result.keynames.update(values)
        return result
    
    def drop_column(self, *columns: str) -> Self:
        if not columns:
            return deepcopy(self)
        assert all(column in self.columns for column in columns)
        df = self.table.df if self.filter.indices is None else self.table.df.loc[self.filter.indices]
        for column in columns:
            df = df.drop(column, axis=1)
        keynames = {name for name in self.keynames if name not in columns}
        return type(self)(_Table(df), keynames=keynames, **self.filters_kwargs())

    def clone_append(self, 
        subtable: Optional["FilteredTable"], 
        dtypes: dict[str, type] | None = None, 
        **values: Scalar | Sequence[Scalar]
    ) -> Self:
        """ Appends a subtable to a returned table, without modifying self.
        WARNING: if subtable is None, the returned table is self. """
        return self if not subtable else self | subtable.add_columns(dtypes, **values)

    def __setitem__(self, index: np.int64, value: TableRow | Mapping[str, Scalar] | Sequence[Scalar]):
        self.set_series(index, self.row2series(value))
    
    def set_series(self, index: np.int64, series: pd.Series | Mapping[str, Scalar]):
        # remove index from filter and _cache
        self.table.set_row(index, series)
        self.table_version += 1
        self.filter.remove_index(index)
        if not self.filter.must_be_filtered_out(series):
            self.filter.add_index(index)
    
    def set(self, 
        row: TableRow | pd.Series | None = None, 
        keynames: Iterable[str] | None = None, 
        **values: Scalar
    ):
        """ This method aims to guarantee keynames uniqueness. Replacing last is our best effort. """
        if row is None:
            kwargs = dict()
        elif isinstance(row, pd.Series):
            kwargs = row.to_dict()
        else:
            kwargs = self.row2series(row).to_dict()
        default = self.TableRowType.default
        assert isinstance(default, dict)
        kwargs = default | kwargs | values
        
        keynames = self.keynames if keynames is None else keynames
        keys = {name: key for name, key in kwargs.items() if name in keynames}
        
        index = self.get_index("last", **keys) if self.default_select == "unique" else None
        if index is None:
            self.append_series(kwargs)
        else:
            self.set_series(index, kwargs)

    def append(self, 
        row: pd.Series | TableRow | Mapping[str, Scalar] | Sequence[Scalar] | None = None, 
        **values: Scalar
    ):
        if row is None:
            series = pd.Series(values)
        else:
            series = row if isinstance(row, pd.Series) else self.row2series(row)
            for name, value in values.items():
                series[name] = value
        for name, value in values.items():
            series[name] = value
        self.append_series(series)
    
    def append_series(self, row: pd.Series | Mapping[str, Scalar]):
        index = len(self.table)
        self.table.append_row(row)
        self.table_version += 1
        if self.filter and not self._must_be_filtered_out(row):
            self.filter.add_index(np.int64(index))

    def __ior__(self, other: Union["FilteredTable", Sequence[pd.Series | Mapping[str, Scalar]]]):
        for other_series in (other._iter_series() if isinstance(other, FilteredTable) else other):
            self.append_series(other_series)

    @classmethod
    def get_dtype(cls, dtype: DTypeLike | str) -> DTypeLike:
        if isinstance(dtype, DTypeLike): # type: ignore
            return dtype
        if dtype in {"float", "float64", "np.float64", "numpy.float64"}:
            return np.float64
        if dtype in {"float32", "np.float32", "numpy.float32"}:
            return np.float32
        if dtype in {"float16", "np.float16", "numpy.float16"}:
            return np.float16
        if dtype in {"int", "int64", "np.int64", "numpy.int64"}:
            return np.int64
        if dtype in {"int32", "np.int32", "numpy.int32"}:
            return np.int32
        if dtype in {"int16", "np.int16", "numpy.int16"}:
            return np.int16
        if dtype in {"int8", "np.int8", "numpy.int8"}:
            return np.int8
        if dtype in {"uint", "uint64", "np.uint64", "numpy.uint64"}:
            return np.uint64
        if dtype in {"uint32", "np.uint32", "numpy.uint32"}:
            return np.uint32
        if dtype in {"uint16", "np.uint16", "numpy.uint16"}:
            return np.uint16
        if dtype in {"uint8", "np.uint8", "numpy.uint8"}:
            return np.uint8
        if dtype == "bool":
            return bool
        if dtype == "str":
            return str
        if dtype == "object":
            return object
        raise ValueError(dtype)
    @classmethod
    def get_dtypes(cls, dtypes: dict[str, DTypeLike | str] | None = None) -> dict[str, DTypeLike]:
        return cls.default_dtypes | {n: cls.get_dtype(t) for n, t in (dtypes or dict()).items()}
    @classmethod
    def dtype_to_str(cls, dtype: type | str) -> str:
        if isinstance(dtype, str):
            return dtype
        if dtype == np.float64 or dtype == float:
            return "float"
        if dtype == np.float32:
            return "float32"
        if dtype == np.float16:
            return "float16"
        if dtype == np.int64 or dtype == int: # always use int64 rather than int
            return "int64"
        if dtype == np.int32:
            return "int32"
        if dtype == np.int16:
            return "int16"
        if dtype == np.int8:
            return "int8"
        if dtype == np.uint64:
            return "uint64"
        if dtype == np.uint32:
            return "uint32"
        if dtype == np.uint16:
            return "uint16"
        if dtype == np.uint8:
            return "uint8"
        if dtype == bool:
            return "bool"
        if dtype == str:
            return "str"
        if dtype == object:
            return "object"
        raise ValueError(dtype)
    def dtypes_to_str_dict(self) -> dict[str, str]:
        return {str(n): self.dtype_to_str(t) for n, t in self.table.df.dtypes.items()}

    @classmethod
    def load(cls, 
        directory: str | Path, 
        source: str | None = None, 
        **kwargs: Any
    ) -> Self:
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
        save_instructions: bool = False
    ) -> tuple[str, dict[str, Any]]:
        """ Argument save_instructions is used for consistency with MultiKeyTable and Objects """
        source = source or f"{self.name}.parquet"
        if not directory:
            return self.save_instructions(source, directory, save_instructions)
        path = f"{directory}/{source}"
        if source.endswith(".parquet"):
            self.table.df.to_parquet(path)
        elif source.endswith(".csv"):
            self.table.df.to_csv(path)
        return self.save_instructions(source, directory, save_instructions)
    
    def save_instructions(self, 
        source: str | None = None, 
        directory: str | Path | None = None, 
        save_instructions: bool=True,
    ) -> tuple[str, dict[str, Any]]:
        source = source or f"{self.name}.parquet"
        kwargs = dict(source=source, dtypes=self.dtypes_to_str_dict())
        instructions = type(self).__name__, kwargs
        if directory and save_instructions:
            filename = (".".join(source.split(".")[:-1]) + ".yaml") if "." in source else f"{source}.yaml"
            with open(Path(directory) / filename, "w") as f:
                yaml.safe_dump(instructions, f)
        return instructions

    def requires_save_instructions(self) -> bool:
        return False # default value
    
    def __repr__(self, show_cache: bool = False) -> str:
        r = f"{self.name} ({len(self)} rows)\n"
        if not self:
            return r + "empty table (no row)\n"
        r += f"{repr(self.filter)}\n"
        if show_cache:
            r += f"{self.table.repr_cache()}\n"
        return r + repr(self.table.df.loc[self.indices] if self.filter else self.table.df)


class RowFilteredTable(FilteredTable[Row]):
    pass