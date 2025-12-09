from abc import ABC, abstractmethod
from typing import Iterable
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

import numpy as np

from solidago.poll import *
from solidago.modules.base import PollFunction
from solidago.poll.user_clusters.base import UserClusters


class UserClustering(PollFunction, ABC):
    def __init__(self, 
        pca_dimension: int | None=None, 
        n_clusters: int | Iterable=range(2, 5), 
        *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.pca_dimension = pca_dimension
        self.n_clusters = n_clusters
    
    def __call__(self, 
        users: Users, 
        entities: Entities, 
        user_models: UserModels
    ) -> tuple[Users, dict[str, UserClusters]]:
        clusters = dict()
        for criterion in user_models.criteria():
            users, c = self.cluster(users, entities, criterion, user_models)
            clusters[criterion] = c
        return users, clusters

    def cluster(self, 
        users: Users, 
        entities: Entities, 
        criterion: str,
        user_models: UserModels
    ) -> tuple[Users, UserClusters]:
        matrix, _, _ = user_models.to_matrices(users, entities, criterion)
        if self.pca_dimension:
            matrix = PCA(n_components=self.pca_dimension).fit_transform(matrix)
        clusters, cluster_assignment = self.matrix2clusters(matrix)
        clusters = UserClusters([users[{users.index2name(i) for i in c}] for c in clusters])
        return users.assign(**{f"cluster_assignment_{criterion}": cluster_assignment}), clusters
    
    def matrix2clusters(self, 
        matrix: np.ndarray, 
        n_clusters: int | Iterable | None=None,
    ) -> tuple[set[int], list[int]]:
        n_clusters = n_clusters or self.n_clusters
        if not isinstance(n_clusters, int):
            assert isinstance(n_clusters, Iterable)
            return self.cluster_optimize(matrix, n_clusters)
        cluster_assignment = KMeans(n_clusters=n_clusters).fit(matrix).labels_
        clusters = [ set() for _ in range(n_clusters) ]
        for user_index, cluster_index in enumerate(cluster_assignment):
            clusters[cluster_index].add(user_index)
        return clusters, cluster_assignment

    def cluster_optimize(self, 
        points: np.ndarray, 
        n_clusters_set: Iterable | None=None
    ) -> tuple[list[set], np.ndarray]:
        n_clusters_set = n_clusters_set or self.n_clusters
        top_score, top_clusters, top_cluster_assignment = -float("inf"), None, None
        for n_clusters in n_clusters_set:
            if n_clusters > len(points):
                continue
            clusters, cluster_assignment = self.cluster(points, n_clusters)
            score = self.clustering_score(points, clusters, cluster_assignment)
            if score > top_score:
                top_score, top_clusters, top_cluster_assignment = score, clusters, cluster_assignment
        return clusters, cluster_assignment

    def clustering_score(self, 
        matrix: np.ndarray, 
        clusters: list[set], 
        cluster_assignment: list[int]
    ) -> float:
        silhouette = (
            silhouette_score(matrix, cluster_assignment)
            if len(np.unique(clusters)) > 1
            else -1
        )
        group_sizes = [len(cluster) for cluster in clusters]
        size_balance = np.min(group_sizes) / np.max(group_sizes)
        cluster_mean_distances = self.compute_cluster_mean_distances(matrix, clusters)
        return silhouette * 0.4 + size_balance * 0.3 + cluster_mean_distances * 0.3

    def compute_cluster_mean_distances(self, matrix: np.ndarray, clusters: list[set]) -> np.ndarray:
        cluster_means = [np.mean(matrix[list(cluster)], axis=0) for cluster in clusters]
        return np.mean([
            np.linalg.norm(cluster_means[i] - cluster_means[j])
            for i in range(len(clusters))
            for j in range(i)
        ])


