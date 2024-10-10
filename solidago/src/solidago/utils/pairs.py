from typing import Union

import numpy as np


class UnorderedPairs:
    def __init__(self, elements: Union[list, int]):
        if isinstance(elements, int):
            self.elements = np.arange(elements)
        else:
            self.elements = elements

    @property
    def n_elements(self):
        return len(self.elements)

    @property
    def n_pairs(self):
        return (self.n_elements * (self.n_elements - 1)) // 2

    def __iter__(self):
        return UnorderedPairsIterator(self)

    def index_to_pair(self, index: int, p_shuffle: Union[int, float] = 0):
        assert index >= 0 and index < self.n_pairs
        a = int((1 + np.sqrt(8 * index + 1)) / 2)
        b = index - int(a * (a - 1) / 2)
        try:
            self.elements[b]
        except:
            raise ValueError(b)
        return swap(self.elements[a], self.elements[b], p_shuffle)

    def sample(self, p_shuffle=0.5) -> tuple[int, int]:
        index = np.random.randint(self.n_elements)
        return self.index_to_pair(index, p_shuffle)

    def n_samples(self, n_samples: int, p_shuffle: float = 0.5) -> list[tuple[int, int]]:
        indices = np.arange(self.n_pairs)
        np.random.shuffle(indices)
        return [self.index_to_pair(index, p_shuffle) for index in indices[:n_samples]]


class UnorderedPairsIterator:
    def __init__(self, pairs):
        self.pairs = pairs
        self.a, self.b = 0, -1

    def __next__(self):
        self.b += 1
        if self.a == self.b:
            self.a += 1
            self.b = 0
        if self.a >= self.pairs.n_elements:
            raise StopIteration
        return self.pairs.elements[self.a], self.pairs.elements[self.b]


def swap(a, b, p_shuffle: Union[float, int] = 1):
    if p_shuffle == 0:
        return a, b
    if p_shuffle == 1 or np.random.random() <= p_shuffle:
        return b, a
    return a, b
