import numpy as np

from solidago.primitives.datastructure.vector_dataframe import VectorSeries, VectorDataFrame


class VectorEntity(VectorSeries):
    def __init__(self, vector: np.ndarray, *args, **kwargs):
        super().__init__(vector, *args, **kwargs)


class VectorEntities(VectorDataFrame):
    index_name = "entity_name"
    series_cls = VectorEntity

    def __init__(self, vectors: np.ndarray, *args, **kwargs):
        super().__init__(vectors, "entities.csv", "entity_vectors.csv", *args, **kwargs)
