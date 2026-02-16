from typing import Any, Iterable, Iterator, TypeVar, Generic

import numpy as np


T = TypeVar("T")

class UnorderedPairs(Generic[T]):
    def __init__(self, elements: Iterable[T] | int):
        if isinstance(elements, int):
            self.elements = np.arange(elements)
        else:
            self.elements = list(elements)

    @property
    def n_elements(self) -> int:
        return len(self.elements)

    @property
    def n_pairs(self) -> int:
        return (self.n_elements * (self.n_elements - 1)) // 2

    def __iter__(self) -> Iterator[tuple[T, T]]:
        for index, e in enumerate(self.elements):
            for f in self.elements[:index]:
                yield e, f

    def index_to_pair(self, index: int, p_shuffle: int | float = 0) -> tuple[T, T]:
        assert index >= 0 and index < self.n_pairs
        a = int((1 + np.sqrt(8 * index + 1)) / 2)
        b = index - int(a * (a - 1) / 2)
        try:
            self.elements[b]
        except:
            raise ValueError(b)
        return swap(self.elements[a], self.elements[b], p_shuffle)

    def sample(self, p_shuffle: float=0.5) -> tuple[T, T]:
        index = np.random.randint(self.n_elements)
        return self.index_to_pair(index, p_shuffle)

    def n_samples(self, n_samples: int, p_shuffle: float = 0.5) -> list[tuple[Any, Any]]:
        indices = np.arange(self.n_pairs)
        np.random.shuffle(indices)
        return [self.index_to_pair(index, p_shuffle) for index in indices[:n_samples]]


def swap(a: T, b: T, p_shuffle: float | int = 1) -> tuple[T, T]:
    if p_shuffle == 0:
        return a, b
    if p_shuffle == 1 or np.random.random() <= p_shuffle:
        return b, a
    return a, b
