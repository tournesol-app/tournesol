from typing import Optional, Callable, Union, Any
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
        return Comparison(- self.value, self.max, self.location)


class Comparisons(MultiKeyTable):
    name: str="comparisons"
    value_factory: Callable=lambda: None
    value_cls: type=Comparison
    
    def __init__(self, 
        keynames: list[str]=["username", "criterion", "entity_name", "other_name"], 
        init_data: Optional[Union[NestedDict, Any]]=None,
        parent_tuple: Optional[tuple["Comparisons", tuple, tuple]]=None,
        *args, **kwargs
    ):
        super().__init__(keynames, init_data, parent_tuple, *args, **kwargs)

    def value2series(self, comparison: Comparison) -> Series:
        return comparison.to_series()
    
    def series2value(self, previous_value: Any, row: Series) -> Comparison:
        return Comparison.from_series(row)

    def _keys(self, **kwargs) -> tuple[tuple, tuple]:
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

    def set(self, *args, **kwargs) -> None:
        """ args is assumed to list keys and then value, 
        though some may be specified through kwargs """
        assert len(args) + len(kwargs) == self.depth + 1
        if "value" not in kwargs: # args[-1] is value
            value = args[-1]
            args = args[:-1]
        else:
            assert "value" in kwargs
            value = kwargs["value"]
            del kwargs["value"]
        kwargs = self.keys2kwargs(*args, **kwargs)
        self._main_cache()
        for keynames in self._cache:
            keys1, keys2 = self._keys(**kwargs)
            self._cache[keynames][keys1] = value
            self._cache[keynames][keys2] = - value
        if self.parent: # Required because child may have created a cache absent from parent
            kwargs = kwargs | dict(zip(self.parent_keynames, self.parent_keys))
            self.parent.set(value, **kwargs)
    
    def to_df(self) -> DataFrame:
        try:
            entity_name_index = self.keynames.index("entity_name")
            other_name_index = self.keynames.index("other_name")
            return DataFrame([ 
                Series(dict(zip(self.keynames, keys)) | dict(self.value2series(comparison)))
                for keys, comparison in self
                if comparison.location == "left"
            ]).rename({ "entity_name": "left_name", "other_name": "right_name" })
        except ValueError:
            return super().to_df()

    def get_evaluators(self, entity: Union[str, "Entity"]) -> set:
        self.nested_dict("entity_name", "username")
        return self.get(entity_name=str(entity)).keys("username")

    def compared_entity_indices(self, entities: "Entities") -> defaultdict[int, list]:
        """ Returns a dict, where dict[i] is a list of j,
        which correspond to the indices of the entities that i was compared to """
        entity_keys_index = self.keynames.index("entity_name")
        other_keys_index = self.keynames.index("other_name")
        d = defaultdict(list)
        for keys in self.keys():
            entity_index = entities.name2index[keys[entity_keys_index]]
            other_index = entities.name2index[keys[other_keys_index]]
            d[entity_index].append(other_index)
        return d

    def normalized_comparisons(self, entities: "Entities") -> defaultdict[int, list]:
        entity_keys_index = self.keynames.index("entity_name")
        d = defaultdict(list)
        for keys, comparison in self:
            entity_index = entities.name2index[keys[entity_keys_index]]
            d[entity_index].append(comparison.value / comparison.max)
        return d
