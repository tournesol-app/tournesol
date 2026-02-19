from typing import Iterable


def to_criteria(criterion: str | Iterable[str]) -> set[str]:
    return {criterion} if isinstance(criterion, str) else set(criterion)