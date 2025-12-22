from copy import deepcopy
from typing import Callable
import yaml


class Record:
    ValueType = list | dict | str | int | float | bool
    KeyType = int | str | list[int | str]

    def __init__(self, value: ValueType):
        assert isinstance(value, Record.ValueType)
        if isinstance(value, list):
            for v in value:
                Record(v) # test if subvalues are Instructions
        if isinstance(value, dict):
            for v in value.values():
                Record(v) # test if subvalues are Instructions
        if isinstance(value, str) and value.startswith("range("):
            value = Record._parse_range(value)
        self.value = value
    @classmethod
    def load(cls, filename: str) -> "Record":
        with open(filename) as f:
            return Record(yaml.safe_load(f))
        
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


    def parse_keys(keys: KeyType) -> list[int | str]:
        """ Idempotent method """
        if isinstance(keys, str):
            return keys.split(".")
        elif isinstance(keys, int):
            return [keys]
        assert isinstance(keys, list)
        return keys
    def has(self, keys: KeyType) -> bool:
        keys = Record.parse_keys(keys)
        if not keys:
            return True
        if not isinstance(self.value, (list, dict)):
            return False
        try:
            key = keys[0] if isinstance(self.value, dict) else int(keys[0])
            value = self.value[key]
            return Record(value).has(keys[1:])
        except (ValueError, IndexError):
            return False
    def __getitem__(self, keys: KeyType) -> ValueType:
        keys = Record.parse_keys(keys)
        if not keys:
            return self.value
        assert isinstance(self.value, (list, dict)), (keys, self.value)
        try:
            key = keys[0] if isinstance(self.value, dict) else int(keys[0])
            value = self.value[key]
            return Record(value)[keys[1:]]
        except (ValueError, IndexError): 
            raise ValueError(keys, self.value)
    def __setitem__(self, keys: KeyType, value: ValueType):
        keys = Record.parse_keys(keys)
        assert len(keys) > 0, keys # cannot have empty keys list
        key = keys[0] if isinstance(self.value, dict) else int(keys[0])
        if len(keys) == 1:
            self.value[key] = value
        else:
            Record(self.value[key])[keys[1:]] = value

    def parse_variables(self, variables: list[str] | list[list[str]] | None) -> tuple[list[list[str]], list[list]]:
        """ Returns varnames, varvalues """
        parsed = [self.parse_variable(v) for v in (variables or list())]
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
                values = Record._parse_range(values) if values.startswith("range(") else [values]
            else:
                values = variable[1].split(" ")
            return varnames, values
        varnames = variable.split(" ")
        values = self[varnames[0]]
        assert isinstance(values, (str, list))
        if isinstance(values, str):
            values = Record._parse_range(values) if values.startswith("range(") else [values]
        return varnames, values
    
    def clone(self) -> "Record":
        return Record(deepcopy(self.value))

    def extract_indices(self, varnames: list[list[str]], varname_values: list, indices: list[int], varname_index: int = 0) -> "Record":
        assert len(varnames) == len(varname_values), (varnames, varname_values)
        assert len(varnames) == len(indices), (varnames, indices)
        result = deepcopy(self.value)
        varname, varname_value = varnames[0][0], varname_values[0][indices[0]]
        if result.has(varname):
            result[varname] = Record.value_extract(result[varname], varname_value, indices[0], varname_index)
        if len(varnames[0]) == 1 and len(varnames) == 1: # ready to return
            return result
        elif len(varnames[0]) > 1:
            varnames[0] = varnames[0][1:]
            return result.extract_indices(varnames, varname_values, indices, varname_index)
        return result.extract_indices(varnames[1:], varname_values[1:], indices[1:], varname_index + 1)
    
    def _value_extract(values, varname_value: str, index: int, varname_index: int) -> ValueType:
        if isinstance(values, list):
            assert len(values) > index, (index, values)
            return values[index]
        if isinstance(values, str):
            def f(inner_brackets):
                try:
                    if int(inner_brackets) != varname_index:
                        raise ValueError()
                    return varname_value
                except:
                    return "{" + inner_brackets + "}"
            return map_brackets(values, f)
        return values

def parse_brackets(text: str, brackets: str = "{}") -> tuple[list[str], list[str]]:
    """ Decompose text into substrings. 
    The first list contains out of brackets. It initiates the sequence, potentially with "".
    The second list contains interleaved in-bracket texts. """
    assert len(brackets) == 2, brackets # must have an open and a close symbol, which could be the same
    out_brackets, in_brackets, index = list(), list(), 0
    while brackets[0] in text[index:]:
        open_bracket_index = index + text[index:].index(brackets[0])
        if brackets[1] not in text[open_bracket_index:]:
            break 
        closed_bracket_index = open_bracket_index + text[open_bracket_index:].index(brackets[1])
        out_brackets.append(text[index:open_bracket_index])
        in_brackets.append(text[open_bracket_index+1:closed_bracket_index])
        index = closed_bracket_index + 1
    out_brackets.append(text[index:])
    return out_brackets, in_brackets
def interleave_texts(texts1: list[str], texts2: list[str]) -> str:
    assert len(texts1) == len(texts2) or len(texts1) == len(texts2) + 1
    interleaved = [i for pair in zip(texts1[:len(texts2)], texts2) for i in pair]
    if len(texts1) == len(texts2) + 1:
        interleaved.append(texts1[-1])
    return "".join(interleaved)
def map_brackets(text: str, function: Callable, brackets: str = "{}") -> str:
    out_brackets, in_brackets = parse_brackets(text, brackets)
    filled_in_brackets = [function(text) for text in in_brackets]
    return interleave_texts(out_brackets, filled_in_brackets)
