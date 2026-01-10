from typing import Optional, Iterable, Union, Any, TYPE_CHECKING
from pandas import Series, DataFrame
from collections import defaultdict

import numpy as np

from solidago.primitives.datastructure import NestedDict, MultiKeyTable

if TYPE_CHECKING:
    from solidago.poll.entities import Entity, Entities


class Comparison:
    def __init__(self, value: float=float("nan"), max: float=float("inf"), location: str="left", **kwargs):
        self.value = value
        self.max = max
        self.location = location
    
    @classmethod
    def from_series(cls, row: Series) -> "Comparison":
        return cls(**dict(row))

    @property
    def keynames(self) -> tuple:
        return "value", "max", "location"

    def to_tuple(self) -> tuple:
        return self.value, self.max, self.location
    
    def to_series(self) -> Series:
        return Series(dict(zip(self.keynames, self.to_tuple())))
    
    def __neg__(self) -> "Comparison":
        location = "right" if self.location == "left" else "left"
        return Comparison(- self.value, self.max, location)

    def __repr__(self) -> str:
        return f"{self.value} (max={self.max}, location={self.location})"


class Comparisons(MultiKeyTable):
    name: str="comparisons"
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

    @property
    def valuenames(self) -> tuple:
        return self.value_cls().keynames

    def value2tuple(self, comparison: Comparison) -> tuple:
        return comparison.to_tuple()
    
    def series2value(self, previous_value: Any, row: Series) -> Comparison:
        return Comparison.from_series(row)

    def _keys(self, *args, keynames: Optional[str]=None, **kwargs) -> tuple[tuple, tuple]:
        keynames = keynames or self.keynames
        kwargs = self.keys2kwargs(*args, **kwargs)
        keys1, keys2 = list(), list()
        for keyname in keynames:
            keys1.append(kwargs[keyname])
            if keyname == "entity_name" and "other_name" in kwargs:
                keys2.append(kwargs["other_name"])
            elif keyname == "other_name" and "entity_name" in kwargs:
                keys2.append(kwargs["entity_name"])
            elif keyname == "left_name" and "right_name" in kwargs:
                keys2.append(kwargs["right_name"])
            elif keyname == "right_name" and "left_name" in kwargs:
                keys2.append(kwargs["right_name"])
            else:
                keys2.append(kwargs[keyname])
        return tuple(keys1), tuple(keys2)
        
    def _main_cache(self) -> NestedDict:
        """ This method is complicated because it handles multiple structures of self.init_data 
        to construct a first main cache that corresponds to self.keynames
        """
        if self.keynames in self._cache:
            return self._cache[self.keynames]
        d = self._init_data_to_dict()
        self._cache[self.keynames] = NestedDict(type(self).value_factory, self.depth)
        for keys, value in d.items():
            keys1, keys2 = self._keys(*keys)
            self._cache[self.keynames][keys1] = value
            self._cache[self.keynames][keys2] = - value
        return self._cache[self.keynames]

    def set(self, *args, **kwargs) -> None:
        """ args is assumed to list keys and then value, 
        though some may be specified through kwargs """
        assert len(args) + len(kwargs) == self.depth + 1
        if "value" in kwargs:
            value = kwargs["value"]
            del kwargs["value"]
        else:
            args, value = args[:-1], args[-1]
        assert isinstance(value, type(self).value_cls)
        kwargs = self.keys2kwargs(*args, **kwargs)
        self._main_cache()
        for keynames in self._cache:
            keys1, keys2 = self._keys(keynames=keynames, **kwargs)
            self._cache[keynames][keys1] = value
            self._cache[keynames][keys2] = - value
        if self.parent: # Required because child may have created a cache absent from parent
            kwargs = kwargs | dict(zip(self.parent_keynames, self.parent_keys))
            self.parent.set(value, **kwargs)
    
    def delete(self, *args, tolerate_key_error: bool=False, **kwargs) -> None:
        kwargs = self.keys2kwargs(*args, **kwargs)
        for keynames in self._cache:
            keys = [kwargs[kn] for kn in keynames]
            try:
                del self._cache[keynames][keys]
            except KeyError as e:
                if not tolerate_key_error:
                    raise e
        if self.parent: # Required because parent may have created a cache absent from child
            kwargs = kwargs | dict(zip(self.parent_keynames, self.parent_keys))
            self.parent.delete(tolerate_key_error=True, **kwargs)

    def to_df(self, max_values: Optional[int]=None) -> DataFrame:
        try:
            entity_name_index = self.keynames.index("entity_name")
            other_name_index = self.keynames.index("other_name")
            data = list()
            for index, (keys, comparison) in enumerate(self.left_right_iter()):
                data.append(Series(dict(zip(self.keynames, keys)) | dict(self.value2series(comparison))))
                if max_values is not None and index > max_values:
                    break
            return DataFrame(data).rename({ "entity_name": "left_name", "other_name": "right_name" })
        except ValueError:
            return super().to_df()

    def left_right_iter(self) -> Iterable:
        for keys, comparison in self:
            if comparison.location == "left":
                yield keys, comparison

    def get_evaluators(self, entity: Union[str, "Entity"]) -> set:
        self.nested_dict("entity_name", "username")
        from solidago.poll.entities import Entity
        entity_name = entity.name if isinstance(entity, Entity) else entity
        return self.get(entity_name=entity_name).keys("username")

    def __len__(self) -> int:
        if isinstance(self.init_data, DataFrame) and "location" not in self.init_data.columns:
            return len(self.init_data)
        return super().__len__() // 2

    def left_right_indices(self, entities: "Entities") -> tuple[list[int], list[int]]:
        """ Returns a dict, where dict[i] is a list of j,
        which correspond to the indices of the entities that i was compared to """
        lk_index, rk_index = self.keynames.index("entity_name"), self.keynames.index("other_name")
        return tuple([
            entities.name2index(keys[key_index])
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
            entity_index = entities.name2index(keys[ek_index])
            d[entity_index].append(entities.name2index(keys[ok_index]))
        return d
        
    def entity_normalized_comparisons(self, entities: "Entities") -> defaultdict[int, list]:
        entity_keys_index = self.keynames.index("entity_name")
        d = defaultdict(list)
        for keys, comparison in self:
            entity_index = entities.name2index(keys[entity_keys_index])
            d[entity_index].append(float(comparison.value / comparison.max))
        return d
