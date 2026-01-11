from typing import Callable, TYPE_CHECKING
from numpy.typing import NDArray
from pandas import DataFrame

import numpy as np

from solidago.primitives.datastructure import MultiKeyTable

if TYPE_CHECKING:
    from solidago.poll import Users, Entities, UserModels, MultiScore

class UserClusters:
    def __init__(self, clusters: list["Users"]):
        self.clusters = clusters
    
    def scores_lists(self, entities: "Entities", user_models: "UserModels") -> MultiKeyTable:
        scores_lists = MultiKeyTable(["cluster", "entity_name", "criterion"])
        scores_lists.value_factory = list
        for cluster in self.clusters:
            for user in cluster:
                for keys, score in user_models[user](entities): # keys == entity_name, criterion
                    if keys not in scores_lists:
                        scores_lists[keys] = list()
                    scores_lists[keys].append(score)
        return scores_lists
    
    def __call__(self, entities: "Entities", user_models: "UserModels", aggregator: Callable) -> MultiScore:
        """ aggregator must be a Callable: *Score -> Score,
        i.e. it must map any list of scores to a score
        """
        scores = MultiScore(["cluster", "entity_name", "criterion"])
        scores_lists = self.scores_lists(entities, user_models)
        for cluster in range(len(self.clusters)):
            for keys, score_list in scores_lists:
                scores[cluster, *keys] = aggregator(*score_list)
        return scores

    def average(self, entities: "Entities", user_models: "UserModels") -> MultiScore:
        from solidago import Score
        return self(entities, user_models, Score.average)

    def std(self, entities: "Entities", user_models: "UserModels") -> MultiScore:
        from solidago import Score
        return self(entities, user_models, Score.std)

    def median(self, entities: "Entities", user_models: "UserModels") -> MultiScore:
        from solidago import Score
        return self(entities, user_models, Score.median)
    
    def characterizing_entities(self, entities: "Entities", user_models: "UserModels") -> "Entities":
        scores = self.average(entities, user_models) # keynames == ["username", "entity_name", "criterion"]

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

def compute_top_comments(identifying_scores: NDArray, comment_means, comments: DataFrame) -> list[list[tuple[str, float]]]:
    top_comments = list()
    for cluster_id in range(identifying_scores.shape[0]):
        top_comments.append(list())
        for comment_id in np.abs(identifying_scores[cluster_id]).argsort()[::-1]:
            comment = [int(comment_id), int(comments.loc[comment_id, "total-votes"]), float(identifying_scores[cluster_id, comment_id])]
            comment += [{cluster: float(comment_means[cluster, comment_id]) for cluster in range(len(comment_means))}]
            comment += [comments.loc[comment_id, "comment"]]
            top_comments[cluster_id].append(comment)
    return top_comments  