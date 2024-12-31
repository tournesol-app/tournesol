import numpy as np

from solidago.primitives.datastructure.vector_dataframe import VectorSeries, VectorDataFrame


class VectorUser(VectorSeries):
    def __init__(self, vector: np.ndarray, *args, **kwargs):
        super().__init__(vector, *args, **kwargs)


class VectorUsers(VectorDataFrame):
    index_name = "username"
    series_cls = VectorUser

    def __init__(self, vectors: np.ndarray, *args, **kwargs):
        super().__init__(vectors, "users.csv", "user_vectors.csv", *args, **kwargs)
