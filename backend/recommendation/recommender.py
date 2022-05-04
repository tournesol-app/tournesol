from core.models import User
from recommendation.graph import Graph
from recommendation.video import Video


class Recommender:
    # Graph containing all videos and existing comparisons, used to get the video preferences
    _complete_graph: Graph
    # Dictionary linking a user to its comparison graph, used to get its information gain
    _user_specific_graphs: dict[User, Graph]

    def get_scale_augmenting_videos(self) -> list[Video]:
        pass

    def do_offline_computation(self):
        scale_aug_vids = self.get_scale_augmenting_videos()
        for g in self._user_specific_graphs.values():
            g.compute_offline_parameters(scale_aug_vids)

    def register_new_user(self, new_user):
        self._user_specific_graphs[new_user] = Graph()

    def register_user_comparison(self, user: User, va: Video, vb: Video):
        self._complete_graph.add_edge(va, vb)
        self._user_specific_graphs[user].add_edge(va, vb)

    def get_first_video_recommendation(self, user: User, nb_video_required: int) -> list[Video]:
        result = []
        sorted_vids = self._user_specific_graphs[user].nodes.sorted()
        for i in range(nb_video_required):
            for v in sorted_vids:
                # TODO : Add max_user_pref attribute to user
                if self._complete_graph.nodes[self._complete_graph.nodes.index(v)].user_pref >= i/nb_video_required * user.max_user_pref:
                    result.append(v)
        return result

    def get_second_video_recommendation(self, user, first_video_id, nb_video_required: int) -> list[Video]:
        result = []
        self._user_specific_graphs[user].graph[first_video_id].sort()
        for i in range(nb_video_required):
            for v in self._user_specific_graphs[user].graph[first_video_id]:
                # TODO : Add max_user_pref attribute to user
                if self._complete_graph.nodes[self._complete_graph.nodes.index(v)].user_pref >= i/nb_video_required * user.max_user_pref:
                    result.append(v)
        return result
