from typing import Callable

class UserClusters:
    def __init__(self, clusters: list["Users"]):
        self.clusters = clusters
    
    # TODO => define methods to analyze the clusters
    def scores(self, entities: "Entities", user_models: "UserModels", aggregator: Callable) -> MultiScore:
        scores = MultiScore(["cluster", "entity_name", "criterion"])
        for cluster in clusters:
            cluster_scores = MultiScore(["entity_name", "criterion"])
            for user in cluster:
                for (entity_name, criterion), score in user_models[user](entities):
                    cluster_scores[entity_name, criterion] = score
            