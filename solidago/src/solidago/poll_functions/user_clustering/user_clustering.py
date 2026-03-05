from typing import Iterable
from numpy.typing import NDArray
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

import numpy as np, pandas as pd

from solidago.poll import *
from solidago.poll_functions.poll_function import PollFunction


class UserClustering(PollFunction):
    def __init__(self, 
        pca_dimension: int | None=None, 
        n_clusters: int | Iterable[int] = range(2, 5), 
        *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.pca_dimension = pca_dimension
        self.n_clusters = n_clusters
    
    def fn(self, users: Users, entities: Entities, user_models: UserModels) -> Users:
        for criterion in user_models.criteria():
            users = self.cluster(users, entities, criterion, user_models)
        return users

    def cluster(self, users: Users, entities: Entities, criterion: str, user_models: UserModels) -> Users:
        matrix, _, _ = user_models.to_matrices(users, entities, criterion)
        if self.pca_dimension:
            matrix = PCA(n_components=self.pca_dimension).fit_transform(matrix)
        cluster_assignment = self.matrix2clusters(matrix)
        return users.assign(**{f"cluster_assignment_{criterion}": cluster_assignment})
    
    def matrix2clusters(self, 
        matrix: NDArray, 
        n_clusters: int | Iterable | None=None,
    ) -> NDArray[np.int64]:
        n_clusters = n_clusters or self.n_clusters
        if not isinstance(n_clusters, int):
            assert isinstance(n_clusters, Iterable)
            return self.cluster_optimize(matrix, n_clusters)
        cluster_assignment = KMeans(n_clusters=n_clusters).fit(matrix).labels_
        clusters = [ set() for _ in range(n_clusters) ]
        for user_index, cluster_index in enumerate(cluster_assignment):
            clusters[cluster_index].add(user_index)
        return cluster_assignment

    def cluster_optimize(self, 
        points: NDArray, 
        n_clusters_set: Iterable[int] | None = None
    ) -> NDArray[np.int64]:
        if n_clusters_set is None:
            n_clusters_set = [self.n_clusters] if isinstance(self.n_clusters, int) else self.n_clusters
        top_score, top_clusters, top_cluster_assignment = -float("inf"), None, None
        for n_clusters in n_clusters_set:
            if n_clusters > len(points):
                continue
            cluster_assignment = self.matrix2clusters(points, n_clusters)
            clusters = [set() for _ in range(np.max(cluster_assignment))]
            for user_index, cluster in enumerate(cluster_assignment):
                clusters[cluster].add(user_index)
            score = self.clustering_score(points, clusters, cluster_assignment)
            if score > top_score:
                top_score, top_cluster_assignment = score, cluster_assignment
        assert top_cluster_assignment is not None
        return top_cluster_assignment

    def clustering_score(self, 
        matrix: NDArray, 
        clusters: list[set], 
        cluster_assignment: list[int] | NDArray[np.int64],
    ) -> float:
        silhouette = (
            silhouette_score(matrix, np.array(cluster_assignment))
            if len(np.unique(cluster_assignment)) > 1
            else -1
        )
        group_sizes = [len(cluster) for cluster in clusters]
        size_balance = np.min(group_sizes) / np.max(group_sizes)
        cluster_mean_distance = self.compute_cluster_mean_distances(matrix, clusters)
        return silhouette * 0.4 + size_balance * 0.3 + cluster_mean_distance * 0.3

    def compute_cluster_mean_distances(self, matrix: NDArray, clusters: list[set]) -> float:
        cluster_means = [np.mean(matrix[list(cluster)], axis=0) for cluster in clusters]
        distances = np.array([
            np.linalg.norm(cluster_means[i] - cluster_means[j])
            for i in range(len(clusters))
            for j in range(i)
        ], dtype=np.float64)
        return distances.mean()


def compute_comment_means(clusters: list[set], vote_matrix: NDArray) -> NDArray:
    return np.array([
        np.mean(vote_matrix[list(cluster)], axis=0)
        for cluster in clusters
    ])

def compute_comment_identifying_scores(comment_means: NDArray) -> NDArray:
    scores = np.zeros(comment_means.shape)
    for comment_id in range(scores.shape[1]):
        means_of_comment = comment_means[:, comment_id]
        cluster_no = means_of_comment.argmin()
        cluster_yes = means_of_comment.argmax()
        mean_of_means = means_of_comment.mean()
        scores[cluster_no, comment_id] = means_of_comment[cluster_no] - mean_of_means
        scores[cluster_yes, comment_id] = means_of_comment[cluster_yes] - mean_of_means
    return scores

def compute_top_comments(identifying_scores: NDArray, comment_means, comments: pd.DataFrame) -> list[list[tuple[str, float]]]:
    top_comments = list()
    for cluster_id in range(identifying_scores.shape[0]):
        top_comments.append(list())
        for comment_id in np.abs(identifying_scores[cluster_id]).argsort()[::-1]:
            comment = [int(comment_id), int(comments.loc[comment_id, "total-votes"]), float(identifying_scores[cluster_id, comment_id])] # type: ignore
            comment += [{cluster: float(comment_means[cluster, comment_id]) for cluster in range(len(comment_means))}]
            comment += [comments.loc[comment_id, "comment"]]
            top_comments[cluster_id].append(comment)
    return top_comments  