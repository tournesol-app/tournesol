from __future__ import annotations

from typing import Optional

import numpy as np
from django.db.models import Avg, F, QuerySet
from scipy.sparse.csgraph import shortest_path

from tournesol.models import (
    ContributorRatingCriteriaScore,
    ContributorScaling,
    EntityCriteriaScore,
    Poll,
)
from tournesol.suggestions.suggested_user import SuggestedUser
from tournesol.suggestions.suggested_user_video import SuggestedUserVideo
from tournesol.suggestions.suggested_video import SuggestedVideo


class CompleteGraph:
    _local_poll: Poll

    LAMBDA_THRESHOLD = 0.5
    MIN_SCALING_ACCURACY = 0.5

    def __init__(self, local_poll: Poll, local_criteria):
        self.local_user_mean: float = 0
        self.dirty = True
        self.edges = []
        self.graph = {}
        self.NEW_NODE_CONNECTION_SCORE = 0.5
        self._nodes = []
        self.uid_to_index = {}
        self._local_poll = local_poll
        self._local_criteria = local_criteria

    @property
    def nodes(self) -> list[SuggestedVideo]:
        return self._nodes

    def add_node(self, new_node: SuggestedVideo):
        if new_node.uid not in self.uid_to_index:
            self._nodes.append(new_node)
            self.graph[new_node] = []
            self.uid_to_index[new_node.uid] = len(self.nodes) - 1
            for n in self._nodes:
                n.nb_comparison_with[new_node.uid] = 0
                new_node.nb_comparison_with[n.uid] = 0
        else:
            print("Warning, trying to insert already present node")

    def add_edge(self, node_a: SuggestedVideo, node_b: SuggestedVideo):
        if node_a not in self._nodes:
            self.add_node(node_a)
        if node_b not in self._nodes:
            self.add_node(node_b)

        node_b.nb_comparison_with[node_a.uid] += 1
        node_a.nb_comparison_with[node_b.uid] += 1

        if node_a <= node_b:
            self.edges.append((node_a, node_b))
            self.graph[node_a].append(node_b)
            self.graph[node_b].append(node_a)
        else:
            self.edges.append((node_b, node_a))
            self.graph[node_a].append(node_b)
            self.graph[node_b].append(node_a)

        self.dirty = True

    def compute_offline_parameters(
            self,
            scaling_factor_increasing_videos: Optional[list[SuggestedVideo]] = None
    ):
        """
        Function computing the offline parameters, including the adjacency matrix, its
        normalization, the distance matrix and the similarity matrix if the graph is a user graph,
        the video scores otherwise
        """
        if self.dirty:
            entity_criteria_scores: QuerySet = (
                EntityCriteriaScore.default_scores().filter(
                    poll__name=self._local_poll.name,
                    criteria=self._local_criteria
                )
                .values("uncertainty", "score", uid=F("entity__uid"))
            )
            for ecs in entity_criteria_scores:
                act_vid = self._nodes[self.uid_to_index[ecs["uid"]]]
                act_vid.video1_score = self.NEW_NODE_CONNECTION_SCORE + ecs["uncertainty"]
                act_vid.global_video_score_uncertainty = ecs["uncertainty"]
                act_vid.global_video_score = ecs["score"]
            self.dirty = False


class Graph(CompleteGraph):
    """
    Class representing a comparison graph
    Each node is a video and each node is a comparison
    """
    # not necessarily the best data structure,
    # I still have to find out what is the best one between the two
    edges: list[tuple[SuggestedVideo, SuggestedVideo]]
    _nodes: list[SuggestedUserVideo]  # todo clean that, use default dict functions
    uid_to_index: dict[str, int]
    graph: dict[SuggestedVideo, list[SuggestedVideo]]
    dirty: bool
    _local_user: SuggestedUser
    local_user_scaling: ContributorScaling

    adjacency_matrix: np.array
    normalized_adjacency_matrix: np.array

    similarity_matrix: np.array

    def __init__(self, local_user: SuggestedUser, local_poll: Poll, local_criteria):
        super().__init__(local_poll, local_criteria)
        self._local_user = local_user

    def add_node(self, new_node: SuggestedVideo):
        if new_node.uid not in self.uid_to_index:
            actual_new_node = SuggestedUserVideo(
                new_node,
                self._local_user
            )
            self.uid_to_index[actual_new_node.uid] = len(self.nodes)
            self._nodes.append(actual_new_node)
            self.graph[actual_new_node] = []
        else:
            print("Warning, trying to insert already present node")

    def add_edge(self, node_a: SuggestedVideo, node_b: SuggestedVideo):
        if node_a not in self._nodes:
            self.add_node(node_a)
        if node_b not in self._nodes:
            self.add_node(node_b)

        if node_a <= node_b:
            self.edges.append((node_a, node_b))
            self.graph[node_a].append(node_b)
            self.graph[node_b].append(node_a)
        else:
            self.edges.append((node_b, node_a))
            self.graph[node_a].append(node_b)
            self.graph[node_b].append(node_a)

        self.dirty = True

    def build_adjacency_matrix(self):
        self.adjacency_matrix = np.zeros((len(self.nodes), len(self.nodes)))
        self.normalized_adjacency_matrix = self.adjacency_matrix.copy()
        degree_matrix = self.adjacency_matrix.copy()

        for u, v in self.edges:
            u_index = self.uid_to_index[u.uid]
            v_index = self.uid_to_index[v.uid]
            self.adjacency_matrix[u_index][v_index] = 1
            self.adjacency_matrix[v_index][u_index] = 1
            degree_matrix[u_index][u_index] += 1
            degree_matrix[v_index][v_index] += 1
        inv_deg_sqrt = np.sqrt(np.linalg.inv(degree_matrix))
        self.normalized_adjacency_matrix = inv_deg_sqrt @ self.adjacency_matrix @ inv_deg_sqrt

    def find_connected_sub_graphs(self) -> set[Graph]:
        visited: list[SuggestedVideo] = []
        waiting_for_visit: list[SuggestedVideo] = []
        future_visits: set[SuggestedVideo]
        unvisited: list[SuggestedVideo] = self.nodes.copy()

        waiting_for_visit.append(unvisited[0])
        result: set[Graph] = set()
        act_graph = Graph(self._local_user, self._local_poll, self._local_criteria)

        while len(unvisited) > 0:
            future_visits = set()
            for act_vid in waiting_for_visit:
                visited.append(act_vid)
                unvisited.remove(act_vid)
                act_graph.add_node(act_vid)
                for v in self.graph[act_vid]:
                    act_graph.add_edge(act_vid, v)
                    if v not in visited and v not in waiting_for_visit and v in unvisited:
                        future_visits.add(v)

            if len(future_visits) == 0 and len(unvisited) > 0:
                result.add(act_graph)
                act_graph = Graph(
                    self._local_user, self._local_poll, self._local_criteria
                )
                future_visits.add(unvisited[0])
            waiting_for_visit = list(future_visits)

        result.add(act_graph)
        return result

    def is_connected(self) -> bool:
        return len(self.find_connected_sub_graphs()) == 1

    def build_similarity_matrix(self):
        distance_matrix = shortest_path(self.adjacency_matrix, directed=False)
        if len(self.nodes) == 0:
            sigma = 1
        else:
            total_max_dist = distance_matrix.max(
                axis=0,
                where=np.isfinite(distance_matrix),
                initial=1
            ).sum()
            sigma = total_max_dist / len(self.nodes)
        self.similarity_matrix = np.exp(-(distance_matrix ** 2) / sigma ** 2)

    def compute_offline_parameters(self, scaling_factor_increasing_videos: list[SuggestedVideo]):
        """
        Function computing the offline parameters, including the adjacency matrix, its
        normalization, the distance matrix and the similarity matrix if the graph is a user graph,
        the video scores otherwise
        """
        if self.dirty:
            self.dirty = False
            self.build_adjacency_matrix()
            self.build_similarity_matrix()
            try:
                self.local_user_scaling = ContributorScaling.objects \
                    .filter(user__id=self._local_user.uid) \
                    .filter(poll__name=self._local_poll.name) \
                    .filter(criteria=self._local_criteria) \
                    .get()
            except ContributorScaling.DoesNotExist:
                self.local_user_scaling = ContributorScaling(
                    scale_uncertainty=0,
                    translation_uncertainty=0
                )
            self.local_user_mean = (
                ContributorRatingCriteriaScore.objects.filter(
                        contributor_rating__user__id=self._local_user.uid)
                .filter(criteria=self._local_criteria)
                .filter(contributor_rating__poll__name=self._local_poll.name)
                .aggregate(mean=Avg("score"))
            )["mean"] or 0.0

            self.compute_information_gain(scaling_factor_increasing_videos)

    def compute_information_gain(self, scaling_factor_increasing_videos: list[SuggestedVideo]):
        """
        Function used to compute the estimated information gain
        """
        # First try to increase the scaling accuracy of the user if necessary
        scale_uncertainty = self.local_user_scaling.scale_uncertainty
        translation_uncertainty = self.local_user_scaling.translation_uncertainty

        weighted_scaling_uncertainty = scale_uncertainty * self.local_user_mean
        actual_scaling_uncertainty = weighted_scaling_uncertainty + translation_uncertainty

        if actual_scaling_uncertainty > self.MIN_SCALING_ACCURACY or len(self.nodes) == 0:
            for va in self._nodes:
                for vb in self._nodes:
                    if (
                            va in scaling_factor_increasing_videos
                            and vb in scaling_factor_increasing_videos
                    ):
                        va.video1_score = 1
                        va._graph_sparsity_score[vb] = 1
                    else:
                        va.video1_score = 0
                        va._graph_sparsity_score[vb] = 0
        # Once the scaling factor is high enough, check what video should gain
        # information being compared by the user
        else:
            sub_graphs = self.find_connected_sub_graphs()
            if len(sub_graphs) == 1:
                sub_graphs = [self]
            for sg in sub_graphs:
                if len(sub_graphs) > 1:
                    sg.compute_offline_parameters(scaling_factor_increasing_videos)
                eigenvalues = np.linalg.eigvalsh(sg.normalized_adjacency_matrix)
                max_beta = 0
                for vb in sg.nodes:
                    for va in self._nodes:
                        # In the case the second highest eigen value is big enough
                        # => the graph is poorly connected,
                        # so we should improve connectivity
                        if eigenvalues[-2] > self.LAMBDA_THRESHOLD:
                            ui = sg.uid_to_index[vb.uid]
                            vi = sg.uid_to_index[va.uid]
                            va._graph_sparsity_score[vb] = 1 - sg.similarity_matrix[ui, vi]
                        elif va.uid not in sg.uid_to_index:
                            va._graph_sparsity_score[vb] = 1
                        else:
                            va._graph_sparsity_score[vb] = 0
                        # Compute estimated information gain relative to the respective
                        # uncertainties in both scores
                        va.beta[vb] = va.uncertainty_diminution(vb)
                        if max_beta < va.beta[vb]:
                            max_beta = va.beta[vb]
                for vb in sg.nodes:
                    vb.suggestibility_normalization = max(max_beta, 1)
