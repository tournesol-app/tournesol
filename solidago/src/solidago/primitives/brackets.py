from typing import Callable


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
    interleaved = [str(i) for pair in zip(texts1[:len(texts2)], texts2) for i in pair]
    if len(texts1) == len(texts2) + 1:
        interleaved.append(texts1[-1])
    return "".join(interleaved)

def map_brackets(text: str, function: Callable, brackets: str = "{}") -> str:
    out_brackets, in_brackets = parse_brackets(text, brackets)
    filled_in_brackets = [function(text) for text in in_brackets]
    return interleave_texts(out_brackets, filled_in_brackets)
