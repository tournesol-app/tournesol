import numpy as np

from solidago.poll import *
from .base import CollaborativeFiltering


class FillWithMeans(CollaborativeFiltering):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def fill(self, 
        value_matrix: np.ndarray, 
        left_matrix: np.ndarray, 
        right_matrix: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        return self.fill_matrix(value_matrix), self.fill_matrix(left_matrix), self.fill_matrix(right_matrix)
    
    def fill_matrix(self, matrix: np.ndarray) -> np.ndarray:
        means = np.nanmean(matrix, axis=0)
        for entity_index, (matrix_column, mean) in enumerate(zip(matrix.T, means)):
            matrix[:, entity_index][np.isnan(matrix_column)] = mean