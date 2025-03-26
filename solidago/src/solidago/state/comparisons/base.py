from typing import Optional, Callable, Iterable, Union, Any
from pandas import Series, DataFrame
from collections import defaultdict

import numpy as np

from solidago.primitives.datastructure import NestedDict, MultiKeyTable


class Comparison:
    def __init__(self, value: float=float("nan"), max: float=float("inf"), location: str="left", **kwargs):
        self.value = value
        self.max = max
        self.location = location
    
    @classmethod
    def from_series(cls, row: Series) -> "Comparison":
        return cls(**dict(row))

    def to_series(self) -> Series:
        return Series(dict(value=self.value, max=self.max))
    
    def __neg__(self) -> "Comparison":
        location = "right" if self.location == "left" else "left"
        return Comparison(- self.value, self.max, location)

    def __repr__(self) -> str:
        return f"{self.value} (max={self.max}, location={self.location})"


class Comparisons(MultiKeyTable):
    name: str="comparisons"
    value_factory: Callable=lambda: None
    value_cls: type=Comparison
    
    def __init__(self, 
        keynames: list[str]=["username", "criterion", "entity_name", "other_name"], 
        init_data: Optional[Union[Any]]=None,
        parent_tuple: Optional[tuple["Comparisons", tuple, tuple]]=None,
        *args, **kwargs
    ):
        if isinstance(init_data, DataFrame):
            init_data = init_data.rename(columns={"left_name": "entity_name", "right_name": "other_name"})
        super().__init__(keynames, init_data, parent_tuple, *args, **kwargs)

    def value2series(self, comparison: Comparison) -> Series:
        return comparison.to_series()
    
    def series2value(self, previous_value: Any, row: Series) -> Comparison:
        return Comparison.from_series(row)

    def _keys(self, *args, **kwargs) -> tuple[tuple, tuple]:
        kwargs = self.keys2kwargs(*args, **kwargs)
        keys1, keys2 = list(), list()
        for keyname in self.keynames:
            keys1.append(kwargs[keyname])
            if keyname in {"entity_name", "left_name"}:
                keys2.append(kwargs["other_name" if keyname == "entity_name" else "right_name"])
            elif keyname in {"other_name", "right_name"}:
                keys2.append(kwargs["entity_name" if keyname == "other_name" else "left_name"])
            else:
                keys2.append(kwargs[keyname])
        return tuple(keys1), tuple(keys2)
        
    def _main_cache(self) -> NestedDict:
        """ This method is complicated because it handles multiple structures of self.init_data 
        to construct a first main cache that corresponds to self.keynames
        """
        if self.keynames in self._cache:
            return self._cache[self.keynames]
        if self._cache:
            keynames, d = next(iter(self._cache.items()))
            assert set(keynames) == set(self.keynames), (keynames, self.keynames)
            self._cache[self.keynames] = NestedDict(type(self).value_factory, self.depth)
            for d_keys, value in d:
                kwargs = { kn: d_keys[kn] for kn in keynames }
                keys1, keys2 = self._keys(**kwargs)
                self._cache[self.keynames][keys1] = value
                self._cache[self.keynames][keys2] = - value
        self._cache[self.keynames] = NestedDict(type(self).value_factory, self.depth)
        if self.init_data is None:
            return self._cache[self.keynames]
        if isinstance(self.init_data, DataFrame):
            for _, row in self.init_data.iterrows():
                keys = tuple(row[kn] for kn in self.keynames)
                value = self.series2value(self._cache[self.keynames][keys], row)
                keys1, keys2 = self._keys(*keys)
                self._cache[self.keynames][keys1] = value
                self._cache[self.keynames][keys2] = - value
            return self._cache[self.keynames]
        kns_and_nd = isinstance(self.init_data, tuple) and len(self.init_data) == 2 
        kns_and_nd = kns_and_nd and isinstance(self.init_data[0], tuple)
        kns_and_nd = kns_and_nd and isinstance(self.init_data[1], NestedDict)
        if kns_and_nd:
            keynames, nested_dict = self.init_data
            for keys, value in nested_dict:
                kwargs = dict(zip(keynames, keys))
                keys1, keys2 = self._keys(**kwargs)
                self._cache[self.keynames][keys1] = value
                self._cache[self.keynames][keys2] = - value
        if isinstance(self.init_data, list):
            for entry in self.init_data:
                assert len(entry) == self.depth + 1
                if isinstance(entry, (tuple, list)):
                    keys, value = tuple(entry[:-1]), entry[-1]
                elif isinstance(entry, dict):
                    assert len(entry) == self.depth + 1
                    keys, value = tuple(entry[kn] for kn in self.keynames), entry["value"]
                keys1, keys2 = self._keys(*keys)
                self._cache[self.keynames][keys1] = value
                self._cache[self.keynames][keys2] = - value
            return self._cache[self.keynames]
        if isinstance(self.init_data, dict):
            for keys, value in self.init_data.items():
                keys1, keys2 = self._keys(*keys)
                self._cache[self.keynames][keys1] = value
                self._cache[self.keynames][keys2] = - value
            return self._cache[self.keynames]
        raise ValueError(f"Type {type(self.init_data)} of raw data {self.init_data} not handled")

    
    def to_df(self) -> DataFrame:
        try:
            entity_name_index = self.keynames.index("entity_name")
            other_name_index = self.keynames.index("other_name")
            return DataFrame([ 
                Series(dict(zip(self.keynames, keys)) | dict(self.value2series(comparison)))
                for keys, comparison in self.left_right_iter()
            ]).rename({ "entity_name": "left_name", "other_name": "right_name" })
        except ValueError:
            return super().to_df()

    def left_right_iter(self) -> Iterable:
        for keys, comparison in self:
            if comparison.location == "left":
                yield keys, comparison

    def get_evaluators(self, entity: Union[str, "Entity"]) -> set:
        self.nested_dict("entity_name", "username")
        return self.get(entity_name=str(entity)).keys("username")

    def left_right_indices(self, entities: "Entities") -> tuple[list[int], list[int]]:
        """ Returns a dict, where dict[i] is a list of j,
        which correspond to the indices of the entities that i was compared to """
        lk_index, rk_index = self.keynames.index("entity_name"), self.keynames.index("other_name")
        return tuple([
            entities.name2index[keys[key_index]]
            for keys, comparison in self.left_right_iter()
        ] for key_index in (lk_index, rk_index))

    def normalized_comparison_list(self) -> list[float]:
        return [ float(comparison.value / comparison.max) for _, comparison in self.left_right_iter()]

    def compared_entity_indices(self, entities: "Entities") -> defaultdict[int, list]:
        """ Returns a dict, where dict[i] is a list of j,
        which correspond to the indices of the entities that i was compared to """
        ek_index, ok_index = self.keynames.index("entity_name"), self.keynames.index("other_name")
        d = defaultdict(list)
        for keys in self.keys():
            entity_index = entities.name2index[keys[ek_index]]
            d[entity_index].append(entities.name2index[keys[ok_index]])
        return d
        
    def entity_normalized_comparisons(self, entities: "Entities") -> defaultdict[int, list]:
        entity_keys_index = self.keynames.index("entity_name")
        d = defaultdict(list)
        for keys, comparison in self:
            entity_index = entities.name2index[keys[entity_keys_index]]
            d[entity_index].append(float(comparison.value / comparison.max))
        return d
