from typing import Union

import numpy as np

from solidago.primitives.datastructure.vector_dataframe import VectorSeries, VectorDataFrame
from .base import Entity, Entities


class VectorEntity(VectorSeries, Entity):
    def __init__(self, vector: np.ndarray, *args, **kwargs):
        super().__init__(vector, *args, **kwargs)


class VectorEntities(VectorDataFrame, Entities):
    series_cls = VectorEntity

    def __init__(self, vectors: Union[np.ndarray, list[VectorSeries]], *args, **kwargs):
        super().__init__(vectors, "entity_vectors.csv", *args, **kwargs)
