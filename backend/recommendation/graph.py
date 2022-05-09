from __future__ import annotations

from recommendation.recomended_user import User
from recommendation.video import Video
import numpy as np


class Graph:
    # not necessarily the best data structure,
    # I still have to find out what is the best one between the two
    edges: list[tuple[Video, Video]]
    _nodes: list[Video]
    graph: dict[Video, list[Video]]
    sigma: float
    dirty: bool
    local_user: User

    LAMBDA_THRESHOLD = 0.5
    MIN_SCALING_ACCURACY = 0.5

    ABSENT_NODE = Video(None)

    adjacency_matrix: np.array
    normalized_adjacency_matrix: np.array

    distance_matrix: np.array
    similarity_matrix: np.array

    @property
    def nodes(self) -> list[Video]:
        return self._nodes

    def __init__(self, local_user):
        self.video_comparison_reference: Video
        self.dirty = True
        # init absent node values
        self.ABSENT_NODE.v1_score = -1
        self.ABSENT_NODE.estimated_information_gains = 1
        self.local_user = local_user

    def add_node(self, new_node):
        if new_node not in self.nodes:
            self.nodes.append(new_node)
            self.graph[new_node] = []
        else:
            print("Warning, trying to insert already present node")

    def add_edge(self, node_a, node_b):
        if node_a not in self.nodes:
            print("Warning ! unknown node added in edge")
        if node_b not in self.nodes:
            print("Warning ! unknown node added in edge")

        node_b.nb_comparison_with[node_a] += 1
        node_a.nb_comparison_with[node_b] += 1
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
            self.normalized_adjacency_matrix[u_index][v_index] = 1 / sum(self.adjacency_matrix[u_index])
            self.normalized_adjacency_matrix[v_index][u_index] = 1 / sum(self.adjacency_matrix[u_index])

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
        visited: list[Video] = []
        waiting_for_visit: list[Video] = [starting_node]
        future_visits: set[Video] = set()
        unvisited: list[Video] = self.nodes.copy()

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
        visited: list[Video] = []
        waiting_for_visit: list[Video] = []
        future_visits: set[Video] = set()
        unvisited: list[Video] = self.nodes.copy()

        waiting_for_visit.append(unvisited.pop())
        result: set[Graph] = set()
        act_graph = Graph()

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
                act_graph = Graph()
                future_visits.add(unvisited.pop())
            waiting_for_visit = list(future_visits)

        result.add(act_graph)
        return result

    def is_connex(self) -> bool:
        return len(self.find_connex_subgraphs()) == 1

    def build_similarity_matrix(self):
        for i, u in enumerate(self.nodes):
            for j, v in enumerate(self.nodes):
                self.similarity_matrix[i][j] = np.e ** ((self.distance_matrix[i, j]) ** 2 / self.sigma ** 2)

    def compute_offline_parameters(self, scaling_factor_increasing_videos):
        if self.dirty:
            self.dirty = False
            self.build_adjacency_matrix()
            self.build_distance_matrix()
            self.build_similarity_matrix()
            self.compute_information_gain(scaling_factor_increasing_videos)

    def compute_information_gain(self, scaling_factor_increasing_videos):
        # First try to increase the scaling accuracy of the user if necessary
        # TODO Use here data from db
        # Contributor_scaling + translation -> yes
        user = self.local_user
        if user.scaling_accuracy * user.mean_score + user.translation_accuracy < self.MIN_SCALING_ACCURACY:
            for v in self.nodes:
                for u in self.nodes:
                    if v in scaling_factor_increasing_videos and u in scaling_factor_increasing_videos:
                        v.v1_score = 1
                        v.v2_score[u] = 1
                    else:
                        v.v1_score = 0
                        v.v2_score[u] = 0
        # Once the scaling factor is high enough, check what video should gain information being compared by the user
        else:
            for sg in self.find_connex_subgraphs():
                eigenvalues = np.linalg.eigvalsh(sg.normalized_adjacency_matrix)
                max_beta = 0
                for u in sg.nodes:
                    for v in self.nodes:
                        # In the case the eigen value is big enough
                        # => the graph is poorly connected,
                        # so we should improve connexity
                        if eigenvalues[1] > self.LAMBDA_THRESHOLD:
                            u_index = sg.nodes.index(u)
                            v_index = sg.nodes.index(v)
                            v.v2_score[u] = sg.similarity_matrix[u_index, v_index]
                        elif v not in sg.nodes:
                            v.v2_score[u] = 1
                        else:
                            v.v2_score[u] = 0
                        # TODO Use here data from db
                        # from rating uncertainty
                        # Attention, filtre par poll + critere (1er critere pour le principal)
                        v.beta[u] += (self.local_user.delta_theta[u] + self.local_user.delta_theta[v] /
                                      (self.local_user.theta[u] - self.local_user.theta[v] + 1))
                        if max_beta < v.beta[u]:
                            max_beta = v.beta[u]
                for u in sg.nodes:
                    for v in self.nodes:
                        v.v2_score[u] += v.beta[u] / max_beta

    # This doesn't depend on the user -> not done here, well actually yes but not used in most of the graphs
    def update_preferences(self):
        for v in self.nodes:
            for u in set(self.graph[v]):
                v.nb_comparison_with[u] = 0
            for u in self.graph[v]:
                v.nb_comparison_with[u] += 1

    def prepare_for_sorting(self, first_video_id: str = ""):
        self.video_comparison_reference.uid = first_video_id
