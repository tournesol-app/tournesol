from abc import ABC, abstractmethod
import numpy as np

from solidago.state import *
from solidago.modules.base import StateFunction


class UserClustering(StateFunction, ABC):
    def __init__(self, 
        pca_dimension: Optional[int]=None, 
        n_clusters: Union[int, tuple[int, int]]=(2, 5), 
        *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.pca_dimension
    
    def __call__(self, users: Users, entities: Entities, user_models: UserModels) -> tuple[Users, UserClusters]:
        matrix, _, _ = user_models.to_matrices(users, entities, criterion)
        if pca_dimension:
            matrix = # TODO
        clusters, cluster_assignment = self.matrix2clusters(matrix)
        clusters = UserClusters([users[{users.index2name(i) for i in c}] for c in clusters])
        return users.assign(cluster_assignment=cluster_assignment), clusters
    
    def matrix2clusters(self, matrix: np.ndarray) -> tuple[set[int], list[int]]:
        # TODO


