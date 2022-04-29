from recommendation.video import Video
import numpy as np


class Graph:
    # not necessarily the best data structure, I still have to find out what is the best one between the two]
    edges: list[tuple[Video, Video]]
    nodes: list[Video]
    graph: dict[Video, list[Video]]
    sigma: float

    adjacency_matrix: np.array
    normalized_adjacency_matrix: np.array

    distance_matrix: np.array
    similarity_matrix: np.array

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
        
        if node_a <= node_b:
            self.edges.append((node_a, node_b))
            self.graph[node_a].append(node_b)
            self.graph[node_b].append(node_a)
        else:
            self.edges.append((node_b, node_a))
            self.graph[node_a].append(node_b)
            self.graph[node_b].append(node_a)

    def build_adjacency_matrix(self):
        self.adjacency_matrix = np.zeroes(len(self.nodes))

        for u, v in self.edges:
            u_index = self.nodes.index(u)
            v_index = self.nodes.index(v)
            self.adjacency_matrix[u_index][v_index] = 1
            self.adjacency_matrix[v_index][u_index] = 1

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
                self.similarity_matrix[i][j] = np.e ** ((self.distance_matrix[i, j])**2/self.sigma**2)
    
    def compute_offline_parameters(self):
        pass

    def compute_information_gain(self):
        pass

    def update_preferences(self):
        pass
