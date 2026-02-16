from numpy.typing import NDArray
import numpy as np

from solidago.poll import *
from .collaborative_filtering import CollaborativeFiltering


class FillWithMeans(CollaborativeFiltering):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def fill(self, 
        value_matrix: NDArray[np.float64], 
        left_matrix: NDArray[np.float64], 
        right_matrix: NDArray[np.float64],
    ) -> tuple[NDArray, NDArray, NDArray]:
        return self.fill_matrix(value_matrix), self.fill_matrix(left_matrix), self.fill_matrix(right_matrix)
    
    def fill_matrix(self, matrix: NDArray[np.float64]) -> NDArray[np.float64]:
        means = np.nanmean(matrix, axis=0)
        for entity_index, (matrix_column, mean) in enumerate(zip(matrix.T, means)):
            matrix[:, entity_index][np.isnan(matrix_column)] = mean
        return means