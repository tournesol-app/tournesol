from numpy.typing import NDArray
import numpy as np

from solidago.poll import *
from .base import CollaborativeFiltering


class FillWithMeans(CollaborativeFiltering):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def fill(self, 
        value_matrix: NDArray, 
        left_matrix: NDArray, 
        right_matrix: NDArray,
    ) -> tuple[NDArray, NDArray, NDArray]:
        return self.fill_matrix(value_matrix), self.fill_matrix(left_matrix), self.fill_matrix(right_matrix)
    
    def fill_matrix(self, matrix: NDArray) -> NDArray:
        means = np.nanmean(matrix, axis=0)
        for entity_index, (matrix_column, mean) in enumerate(zip(matrix.T, means)):
            matrix[:, entity_index][np.isnan(matrix_column)] = mean