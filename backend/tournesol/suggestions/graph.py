from __future__ import annotations

from typing import Optional

import numpy as np
from django.db.models import Avg, QuerySet

from tournesol.models import (
    ContributorRatingCriteriaScore,
    ContributorScaling,
    EntityCriteriaScore,
    Poll,
)
from tournesol.suggestions.suggested_user import SuggestedUser
from tournesol.suggestions.suggested_video import SuggestedVideo


class Graph:
    # not necessarily the best data structure,
    # I still have to find out what is the best one between the two
    edges: list[tuple[SuggestedVideo, SuggestedVideo]] = []
    _nodes: list[SuggestedVideo]
    graph: dict[SuggestedVideo, list[SuggestedVideo]] = {}
    sigma: float
    dirty: bool
    _local_user: SuggestedUser
    local_user_scaling: ContributorScaling
    _local_poll: Poll

    LAMBDA_THRESHOLD = 0.5
    MIN_SCALING_ACCURACY = 0.5

    ABSENT_NODE = SuggestedVideo(None)

    adjacency_matrix: np.array
    normalized_adjacency_matrix: np.array

    distance_matrix: np.array
    similarity_matrix: np.array

    @property
    def nodes(self) -> list[SuggestedVideo]:
        return self._nodes

    def __init__(self, local_user: Optional[SuggestedUser], local_poll: Poll, local_criteria):
        self.local_user_mean: float = 0
        self.video_comparison_reference = SuggestedVideo(None)
        self.dirty = True
        # init absent node values
        self.ABSENT_NODE.v1_score = -1
        self.ABSENT_NODE.estimated_information_gains = 0.75
        self.NEW_NODE_CONNECTION_SCORE = 0.5
        self._local_user = local_user
        self._nodes = []
        self._local_poll = local_poll
        self._local_criteria = local_criteria

    def add_node(self, new_node):
        if new_node not in self.nodes:
            self.nodes.append(new_node)
            self.graph[new_node] = []
            for n in self._nodes:
                n.nb_comparison_with[new_node.uid] = 0
                new_node.nb_comparison_with[n.uid] = 0
        else:
            print("Warning, trying to insert already present node")

    def add_edge(self, node_a: SuggestedVideo, node_b: SuggestedVideo):
        if node_a not in self._nodes:
            print("Warning ! unknown node added in edge")
        if node_b not in self._nodes:
            print("Warning ! unknown node added in edge")

        node_b.nb_comparison_with[node_a.uid] += 1
        node_a.nb_comparison_with[node_b.uid] += 1
        node_a.comparison_nb += 1
        node_b.comparison_nb += 1

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
        self.adjacency_matrix = np.zeroes(len(self.nodes))

        for u, v in self.edges:
            u_index = self.nodes.index(u)
            v_index = self.nodes.index(v)
            self.adjacency_matrix[u_index][v_index] = 1
            self.adjacency_matrix[v_index][u_index] = 1
        for u, v in self.edges:
            u_index = self.nodes.index(u)
            v_index = self.nodes.index(v)
            self.normalized_adjacency_matrix[u_index][v_index] = 1 / sum(
                self.adjacency_matrix[u_index]
            )
            self.normalized_adjacency_matrix[v_index][u_index] = 1 / sum(
                self.adjacency_matrix[u_index]
            )

    def build_distance_matrix(self):
        # Compute sigma here
        self.sigma = 1
        self.distance_matrix = np.zeroes(len(self.nodes))
        total_max_dist = 0
        for i, v in enumerate(self.nodes):
            self.bfs(v, give_distances=True, on_all_sub_graphs=False)
            total_max_dist += max(self.distance_matrix[i])
        self.sigma = total_max_dist / len(self.nodes)

    def bfs(self, starting_node, give_distances=True, on_all_sub_graphs=False):
        visited: list[SuggestedVideo] = []
        waiting_for_visit: list[SuggestedVideo] = [starting_node]
        future_visits: set[SuggestedVideo] = set()
        unvisited: list[SuggestedVideo] = self.nodes.copy()

        act_root = starting_node
        depth = 0

        while len(unvisited) > 0:
            for act_vid in waiting_for_visit:
                # act_vid = waiting_for_visit.pop()
                visited.append(act_vid)
                unvisited.remove(act_vid)
                if give_distances:
                    self.distance_matrix[act_root][act_vid] = depth
                    self.distance_matrix[act_vid][act_root] = depth
                for v in self.graph[act_vid]:
                    if v not in visited and v not in waiting_for_visit:
                        future_visits.add(v)
            if len(future_visits) == 0:
                if on_all_sub_graphs:
                    act_root = unvisited.pop()
                    future_visits.add(act_root)
                    depth = 0
                else:
                    break
            else:
                depth += 1
            waiting_for_visit = list(future_visits)

    def find_connex_subgraphs(self) -> set[Graph]:
        visited: list[SuggestedVideo] = []
        waiting_for_visit: list[SuggestedVideo] = []
        future_visits: set[SuggestedVideo] = set()
        unvisited: list[SuggestedVideo] = self.nodes.copy()

        waiting_for_visit.append(unvisited.pop())
        result: set[Graph] = set()
        act_graph = Graph(self._local_user, self._local_poll, self._local_criteria)

        while len(unvisited) > 0:
            for act_vid in waiting_for_visit:
                # act_vid = waiting_for_visit.pop()
                visited.append(act_vid)
                unvisited.remove(act_vid)
                act_graph.add_node(act_vid)
                for v in self.graph[act_vid]:
                    act_graph.add_edge(act_vid, v)
                    if v not in visited and v not in waiting_for_visit:
                        future_visits.add(v)

            if len(future_visits) == 0:
                result.add(act_graph)
                act_graph = Graph(
                    self._local_user, self._local_poll, self._local_criteria
                )
                future_visits.add(unvisited.pop())
            waiting_for_visit = list(future_visits)

        result.add(act_graph)
        return result

    def is_connex(self) -> bool:
        return len(self.find_connex_subgraphs()) == 1

    def build_similarity_matrix(self):
        for i, u in enumerate(self.nodes):
            for j, v in enumerate(self.nodes):
                exponent = (self.distance_matrix[i, j]) ** 2 / self.sigma**2
                self.similarity_matrix[i][j] = np.e**exponent

    def compute_offline_parameters(self, scaling_factor_increasing_videos: list[SuggestedVideo]):
        if self.dirty and self._local_user is not None:
            self.dirty = False
            self.build_adjacency_matrix()
            self.build_distance_matrix()
            self.build_similarity_matrix()
            self.compute_information_gain(scaling_factor_increasing_videos)
            self.local_user_scaling = ContributorScaling.objects.filter(
                user=self._local_user
            )[0]
            self.local_user_mean = (
                ContributorRatingCriteriaScore.objects.filter(
                    contributor_rating__user=self._local_user
                )
                .filter(contributor_rating__poll_name=self._local_poll.name)
                .aggregate(mean=Avg("score"))["mean"]
            )
        elif self._local_user is None:
            entity_criteria_scores: QuerySet = EntityCriteriaScore.objects.filter(
                comparison__poll__name=self._local_poll.name
            ).filter(criteria=self._local_criteria)
            for ecs in entity_criteria_scores:
                act_vid = self._nodes[self._nodes.index(ecs.entity.uid)]
                act_vid.v1_score = self.NEW_NODE_CONNECTION_SCORE + ecs.uncertainty
                for n in self._nodes:
                    act_vid.v2_score[n] = (
                        self.NEW_NODE_CONNECTION_SCORE + ecs.uncertainty
                    )

    def compute_information_gain(self, scaling_factor_increasing_videos: list[SuggestedVideo]):
        # First try to increase the scaling accuracy of the user if necessary
        user = self._local_user
        scale_uncertainty = self.local_user_scaling.scale_uncertainty
        translation_uncertainty = self.local_user_scaling.translation_uncertainty

        weighted_scaling_uncertainty = scale_uncertainty * self.local_user_mean
        actual_scaling_accuracy = weighted_scaling_uncertainty + translation_uncertainty

        if actual_scaling_accuracy < self.MIN_SCALING_ACCURACY:
            for va in self.nodes:
                for vb in self.nodes:
                    if (
                        va in scaling_factor_increasing_videos
                        and vb in scaling_factor_increasing_videos
                    ):
                        va.v1_score = 1
                        va.v2_score[vb] = 1
                    else:
                        va.v1_score = 0
                        va.v2_score[vb] = 0
        # Once the scaling factor is high enough, check what video should gain
        # information being compared by the user
        else:
            for sg in self.find_connex_subgraphs():
                eigenvalues = np.linalg.eigvalsh(sg.normalized_adjacency_matrix)
                max_beta = 0
                for vb in sg.nodes:
                    for va in self.nodes:
                        # In the case the eigen value is big enough
                        # => the graph is poorly connected,
                        # so we should improve connexity
                        if eigenvalues[1] > self.LAMBDA_THRESHOLD:
                            u_index = sg.nodes.index(vb)
                            v_index = sg.nodes.index(va)
                            va.v2_score[vb] = sg.similarity_matrix[u_index, v_index]
                        elif va not in sg.nodes:
                            va.v2_score[vb] = 1
                        else:
                            va.v2_score[vb] = 0
                        va.beta[vb] += user.delta_theta[vb] + user.delta_theta[va] / (
                            user.theta[vb] - user.theta[va] + 1
                        )
                        if max_beta < va.beta[vb]:
                            max_beta = va.beta[vb]
                for vb in sg.nodes:
                    for va in self.nodes:
                        va.v2_score[vb] += va.beta[vb] / max_beta

    # This doesn't depend on the user -> not done here,
    # well actually yes but not used in most of the graphs
    def update_preferences(self):
        for v in self.nodes:
            for u in set(self.graph[v]):
                v.nb_comparison_with[u.uid] = 0
            for u in self.graph[v]:
                v.nb_comparison_with[u.uid] += 1

    def prepare_for_sorting(self, first_video_id: str = ""):
        self.video_comparison_reference.uid = first_video_id
