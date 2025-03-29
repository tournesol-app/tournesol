from typing import Union, Optional, Callable, Any, Iterable, Literal
from copy import deepcopy


class NestedDict:
    def __init__(self, value_factory: Callable, depth: int):
        assert isinstance(value_factory, Callable) and isinstance(depth, int)
        self.value_factory = value_factory
        self.depth = depth
        self._dict = dict() # self._dict[key] must be dict
        
    def deepcopy(self) -> "NestedDict":
        copy = NestedDict(self.value_factory, self.depth)
        copy._dict = deepcopy(self._dict)
        return copy
        
    def __getitem__(self, keys: Union[tuple, str, int, set, Literal[all]]) -> Union["NestedDict", "Value"]:
        keys = (keys,) if isinstance(keys, (str, int)) else keys
        is_set_or_all = lambda key: isinstance(key, set) or key is all
        if is_set_or_all(keys) or (len(keys) == 1 and is_set_or_all(keys[0])):
            key_set = keys if is_set_or_all(keys) else keys[0]
            filtered = NestedDict(self.value_factory, self.depth)
            filtered._dict = {
                key: subdict for key, subdict in self._dict.items() 
                if key_set is all or key in key_set
            }
            return filtered
        assert len(keys) <= self.depth
        if not keys:
            return self
        if self.depth == 1:
            assert len(keys) == 1
            return self._dict[keys[0]] if keys[0] in self._dict else self.value_factory()
        if is_set_or_all(keys[0]):
            nonset_keys = [key for key in keys if not is_set_or_all(key)]
            nested_dict = NestedDict(self.value_factory, self.depth - len(nonset_keys))
            for key, subdict_dict in self._dict.items():
                if keys[0] is all or key in keys[0]:
                    subdict = NestedDict(self.value_factory, self.depth - 1)
                    subdict._dict = subdict_dict
                    v = subdict[keys[1:]]
                    nested_dict._dict[key] = v._dict if isinstance(v, NestedDict) else v
            return nested_dict
        if keys[0] not in self._dict:
            if len(keys) == self.depth:
                return self.value_factory()
            return NestedDict(self.value_factory, self.depth - len(keys))
        subdict = NestedDict(self.value_factory, self.depth - 1)
        subdict._dict = self._dict[keys[0]]
        return subdict[keys[1:]]
            
    def get_value(self, *args, record_missing_value: bool=True) -> "Value":
        assert len(args) == self.depth
        if args in self:
            return self[args]
        value = self.value_factory()
        if record_missing_value:
            self[args] = value
        return self[args]
    
    def get_keys(self, depths: Union[int, set[int]]=0) -> set:
        depths = depths if isinstance(depths, set) else {depths}
        return {
            tuple(k for i, k in enumerate(keys) if i in depths)
            for keys, value in self.iter(max(depths) + 1)
        }            
        
    def __setitem__(self, keys: tuple, value: Any) -> None:
        keys = (keys,) if isinstance(keys, (str, int)) else keys
        assert len(keys) == self.depth
        subdict = self._dict
        for key in keys[:-1]:
            if key not in subdict:
                subdict[key] = dict()
            subdict = subdict[key]
        subdict[keys[-1]] = value
    
    def __delitem__(self, keys: tuple) -> None:
        keys = (keys,) if isinstance(keys, (str, int)) else keys
        assert len(keys) <= self.depth
        subdict_list = [self._dict]
        for key in keys[:-1]:
            subdict_list.append(subdict_list[-1][key])
        del subdict_list[-1][keys[-1]]
        for index in range(1, len(keys)):
            if not subdict_list[-index]:
                del subdict_list[-index-1][keys[-index-1]]
    
    def __contains__(self, keys: tuple) -> Iterable:
        keys = (keys,) if isinstance(keys, (str, int)) else keys
        subdict = self._dict
        for key in keys:
            if key not in subdict:
                return False
            subdict = subdict[key]
        return True
    
    def __iter__(self) -> Iterable:
        return self.iter(self.depth)

    def iter(self, depth: int) -> Iterable:
        assert depth <= self.depth
        for key, subdict in self._dict.items():
            if depth == 1 and self.depth == 1:
                yield (key,), subdict
            else:
                sub_nested_dict = NestedDict(self.value_factory, self.depth - 1)
                sub_nested_dict._dict = subdict
                if depth == 1:
                    yield (key,), sub_nested_dict
                else:
                    for subkeys, value in sub_nested_dict.iter(depth - 1):
                        yield tuple([key] + list(subkeys)), value

    def __len__(self) -> int:
        return len([x for x in self])
    
    def __bool__(self) -> bool:
        return bool(self._dict)

    def __or__(self, other: "NestedDict") -> "NestedDict":
        assert self.value_factory() == other.value_factory() and self.depth == other.depth
        result = NestedDict(self.value_factory, self.depth)
        result._dict = deepcopy(self._dict)
        for keys, value in other:
            result[keys] = value
        return result

    def __repr__(self) -> str:
        return "NestedDict({\n  " \
            + "\n  ".join([ f"{keys}: {value}" for keys, value in self ]) \
            + "\n})"
