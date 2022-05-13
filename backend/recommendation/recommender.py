from django.db.models import QuerySet

from core.models import User
from recommendation.graph import Graph
from recommendation.video import Video
from tournesol.models import ComparisonCriteriaScore, Entity, Poll


class Recommender:
    # Entity to specific video structure dictionary
    _entity_to_video: dict[Entity, Video] = {}
    _comparison_reference_video: Video = Video(None)
    # Graph containing all videos and existing comparisons, used to get the video preferences
    _complete_graph: Graph
    # Dictionary linking a user to its comparison graph, used to get its information gain
    _user_specific_graphs: dict[User, Graph] = {}

    POLL_NAME = "videos"
    # poll = Poll.default_poll()

    def __init__(self):

        self.poll = Poll.default_poll()
        # build complete graph
        query: QuerySet = ComparisonCriteriaScore.objects.filter(
            comparison__poll__name=self.poll.name
        ).filter(
            criteria=self.poll.criterias_list[0]
        )
        self._complete_graph = Graph(None)

        comparisons = query
        for c in comparisons:
            if c.comparison.entity_1 not in self._entity_to_video.keys():
                self._entity_to_video[c.comparison.entity_1] = Video(self._comparison_reference_video,
                                                                     from_entity=c.comparison.entity_1)
                self._complete_graph.add_node(self._entity_to_video[c.comparison.entity_1])
            if c.comparison.entity_2 not in self._entity_to_video.keys():
                self._entity_to_video[c.comparison.entity_2] = Video(self._comparison_reference_video,
                                                                     from_entity=c.comparison.entity_2)
                self._complete_graph.add_node(self._entity_to_video[c.comparison.entity_2])
            self._complete_graph.add_edge(self._entity_to_video[c.comparison.entity_1],
                                          self._entity_to_video[c.comparison.entity_2])

        # create required user graphs (none at first in fact)

    def get_scale_augmenting_videos(self) -> list[Video]:
        pass

    def do_offline_computation(self):
        # for requests => look at ml->inputs
        scale_aug_vids = self.get_scale_augmenting_videos()
        for g in self._user_specific_graphs.values():
            # Will be cached, do at registration
            g.compute_offline_parameters(scale_aug_vids)

    def register_new_user(self, new_user):
        self._user_specific_graphs[new_user] = Graph(local_user=new_user)
        # build user graph
        query: QuerySet = ComparisonCriteriaScore.objects.filter(
            comparison__poll__name=self.poll.name
        ).filter(
            criteria=self.poll.criterias_list[0]
        ).filter(
            comparison__user__email=new_user.email
        )
        for c in query:
            va = c.comparison.entity_1
            vb = c.comparison.entity_2
            self._user_specific_graphs[new_user].add_edge(va, vb)

    def register_user_comparison(self, user: User, va: Video, vb: Video):
        self._complete_graph.add_edge(va, vb)
        if user in self._user_specific_graphs.keys():
            self._user_specific_graphs[user].add_edge(va, vb)

    def get_first_video_recommendation(self, user: User, nb_video_required: int) -> list[Video]:
        # Lazily load the user graph
        if user not in self._user_specific_graphs.keys():
            self.register_new_user(user)
        result = []
        self._user_specific_graphs[user].prepare_for_sorting()
        considered_vids = set(self._user_specific_graphs[user].nodes)
        tmp = set(self._complete_graph.nodes.copy())
        tmp = tmp.difference(considered_vids)

        considered_vids.update(tmp)
        considered_vids_list = list(considered_vids)
        considered_vids_list.sort(reverse=True)

        max_vid_pref = 0
        for v in considered_vids_list:
            v.user_pref = max(v.nb_comparison_with.values()) / v.comparison_nb
            if v.user_pref > max_vid_pref:
                max_vid_pref = v.user_pref

        for i in range(nb_video_required):
            for v in considered_vids_list:
                act_user_pref = v.user_pref
                if act_user_pref >= (nb_video_required - i) / (nb_video_required + 1) * max_vid_pref:
                    result.append(v)
        return result

    def get_second_video_recommendation(self, user, first_video_id, nb_video_required: int) -> list[Video]:
        # Lazily load the user graphs
        if user not in self._user_specific_graphs.keys():
            self.register_new_user(user)
        result = []
        # TODO Take into account the first video for the info gain
        self._user_specific_graphs[user].prepare_for_sorting(first_video_id)
        considered_vids = set(self._user_specific_graphs[user].nodes)
        tmp = set(self._complete_graph.nodes.copy())
        tmp = tmp.difference(considered_vids)

        considered_vids.update(tmp)
        considered_vids_list = list(considered_vids)
        considered_vids_list.sort(reverse=True)

        max_vid_pref = 0
        for v in considered_vids_list:
            v.user_pref = v.nb_comparison_with[first_video_id] / v.comparison_nb
            if v.user_pref > max_vid_pref:
                max_vid_pref = v.user_pref

        for i in range(nb_video_required):
            for v in considered_vids_list:
                act_user_pref = v.user_pref
                if act_user_pref >= (nb_video_required - i) / (nb_video_required + 1) * max_vid_pref:
                    result.append(v)
        return result
