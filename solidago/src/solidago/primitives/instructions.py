from copy import deepcopy
from typing import Any, Iterator
import yaml

from .brackets import map_brackets

_Value = list | tuple | dict | str | int | float | bool | None
_Key = int | str | tuple[int | str, ...]

class Instructions:
    def __init__(self, value: _Value):
        assert isinstance(value, (list, tuple, dict, str, int, float, bool, type(None))), value
        if isinstance(value, tuple):
            value = list(value)
        if isinstance(value, (list, dict)):
            iterable = enumerate(value) if isinstance(value, list) else value.items()
            for k, v in iterable:
                try:
                    assert isinstance(v, (list, tuple, dict, str, int, float, bool, type(None))), v
                except AssertionError as err:
                    raise ValueError([k], err.args[0])
                except ValueError as err:
                    keys, err_value = err.args
                    raise ValueError(keys + [k], err_value)
        if isinstance(value, str) and value.startswith("range("):
            value = Instructions._parse_range(value)
        self.value = value

    @classmethod
    def load(cls, filename: str) -> "Instructions":
        with open(filename) as f:
            return Instructions(yaml.safe_load(f))
    
    @staticmethod
    def _parse_range(range_txt: str) -> list[int]:
        assert range_txt.startswith("range(") and range_txt[-1] == ")", range_txt
        values = range_txt[6:-1].split(",")
        if len(values) == 1:
            return list(range(int(values[0])))
        if len(values) == 2:
            return list(range(int(values[0]), int(values[1])))
        if len(values) == 3:
            return list(range(int(values[0]), int(values[1]), int(values[2])))
        raise ValueError(f"Failed to parse range {range_txt}")
    def _solve_references(self):
        for keys, value in self:
            if isinstance(value, str) and value.startswith("&"):
                self[keys] = self[value[1:]] # type: ignore
    def is_tuple_cls_kwargs(self) -> bool:
        return isinstance(self.value, list) and len(self.value) == 2 \
            and isinstance(self.value[0], str) and isinstance(self.value[1], dict)

    def __iter__(self) -> Iterator[tuple[tuple[_Key, ...], _Value]]:
        if isinstance(self.value, (str, int, float, bool, type(None))):
            yield (), self.value
        elif isinstance(self.value, list):
            for index, sub in enumerate(self.value):
                assert isinstance(sub, _Value) # type: ignore
                for subkeys, value in Instructions(sub):
                    yield (str(index), *subkeys), value
        else:
            assert isinstance(self.value, dict), self.value
            for key, sub in self.value.items():
                assert isinstance(sub, _Value) # type: ignore
                for subkeys, value in Instructions(sub):
                    yield (key, *subkeys), value

    @staticmethod
    def parse_keys(keys: _Key) -> tuple[int | str, ...]:
        """ Idempotent method """
        if isinstance(keys, str):
            return tuple(keys.split("."))
        elif isinstance(keys, int):
            return (keys,)
        assert isinstance(keys, tuple)
        return keys
    def has(self, keys: _Key) -> bool:
        keys = Instructions.parse_keys(keys)
        if not keys:
            return True
        if not isinstance(self.value, (list, dict)):
            return False
        if self.is_tuple_cls_kwargs() and not keys[0].isdigit(): # type: ignore
            assert isinstance(self.value[1], _Value) 
            return Instructions(self.value[1]).has(keys)
        try:
            key = keys[0] if isinstance(self.value, dict) else int(keys[0])
            return Instructions(self.value[key]).has(keys[1:]) # type: ignore
        except (ValueError, IndexError, KeyError):
            return False
    def __getitem__(self, keys: _Key) -> _Value:
        keys = Instructions.parse_keys(keys)
        if not keys:
            return self.value
        assert isinstance(self.value, (list, dict)), (keys, self.value)
        if self.is_tuple_cls_kwargs() and not keys[0].isdigit(): # type: ignore
            return Instructions(self.value[1])[keys] # type: ignore
        try:
            key = keys[0] if isinstance(self.value, dict) else int(keys[0])
            return Instructions(self.value[key])[keys[1:]] # type: ignore
        except (ValueError, IndexError): 
            raise ValueError(keys, self.value)
    def __setitem__(self, keys: _Key, value: _Value):
        keys = Instructions.parse_keys(keys)
        assert len(keys) > 0, keys # cannot have empty keys list
        if self.is_tuple_cls_kwargs() and not keys[0].isdigit(): # type: ignore
            Instructions(self.value[1])[keys] = value # type: ignore
            return
        key = keys[0] if isinstance(self.value, dict) else int(keys[0])
        if len(keys) == 1:
            self.value[key] = value # type: ignore
        else:
            Instructions(self.value[key])[keys[1:]] = value # type: ignore

    def parse_variables(self, variables: list[str] | list[list[str]] | None) -> tuple[list[list[str]], list[list[Any]]]:
        """ Returns varnames, varvalues """
        parsed: list[tuple[list[str], list[str] | list[int]]] = list()
        for v in (variables or list()):
            try:
                parsed.append(self.parse_variable(v))
            except AssertionError as e:
                raise ValueError(v, e.args[0])
        return [v for v, _ in parsed], [v for _, v in parsed]
    def parse_variable(self, variable: str | list[str]) -> tuple[list[str], list[str] | list[int]]:
        if isinstance(variable, list):
            assert len(variable) == 2
            varnames = variable[0].split(" ")
            if isinstance(variable[1], int) or variable[1].isdigit():
                values = list(range(int(variable[1])))
            elif "." in variable[1]:
                values = self[variable[1]]
                assert isinstance(values, str)
                values = Instructions._parse_range(values) if values.startswith("range(") else [values]
            else:
                values = variable[1].split(" ")
            return varnames, values
        varnames = variable.split(" ")
        values = self[varnames[0]]
        assert isinstance(values, (str, list)), values
        if isinstance(values, str):
            values = Instructions._parse_range(values) if values.startswith("range(") else [values]
        return varnames, values # type: ignore
    
    def clone(self) -> "Instructions":
        return Instructions(deepcopy(self.value))

    def extract_indices(self, 
        varnames: list[list[str]], 
        varname_values: list[list[str]], 
        indices: list[int], 
        varname_index: int = 0
    ) -> "Instructions":
        assert len(varnames) == len(varname_values), (varnames, varname_values)
        assert len(varnames) == len(indices), (varnames, indices)
        result = self.clone()
        if not varnames:
            return result
        varname, varname_value = varnames[0][0], varname_values[0][indices[0]]
        if result.has(varname):
            result[varname] = Instructions._value_extract(result[varname], varname_value, indices[0], varname_index)
        if len(varnames[0]) == 1 and len(varnames) == 1: # ready to return
            result._solve_references()
            return result
        elif len(varnames[0]) > 1:
            varnames[0] = varnames[0][1:]
            return result.extract_indices(varnames, varname_values, indices, varname_index)
        return result.extract_indices(varnames[1:], varname_values[1:], indices[1:], varname_index + 1)
    
    @staticmethod
    def _value_extract(values: list[_Value] | str | _Value, varname_value: str, index: int, varname_index: int) -> _Value:
        if isinstance(values, list):
            assert len(values) > index, (index, values)
            return values[index] # type: ignore
        if isinstance(values, str):
            def f(inner_brackets: str) -> str:
                try:
                    if int(inner_brackets) != varname_index:
                        raise ValueError()
                    return varname_value
                except:
                    return "{" + inner_brackets + "}"
            return map_brackets(values, f)
        return values

