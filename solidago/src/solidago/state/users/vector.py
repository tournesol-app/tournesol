from typing import Union

import numpy as np

from solidago.primitives.datastructure.vector_dataframe import VectorSeries, VectorDataFrame
from .base import User, Users


class VectorUser(VectorSeries, User):
    def __init__(self, vector: np.ndarray, *args, **kwargs):
        super().__init__(vector, *args, **kwargs)


class VectorUsers(VectorDataFrame, Users):
    series_cls = VectorUser

    def __init__(self, vectors: Union[np.ndarray, list[VectorSeries]], *args, **kwargs):
        super().__init__(vectors, "user_vectors.csv", *args, **kwargs)
