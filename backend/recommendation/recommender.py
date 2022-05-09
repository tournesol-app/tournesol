from django.db.models import QuerySet

from core.models import User
from recommendation.graph import Graph
from recommendation.video import Video
from tournesol.models import ComparisonCriteriaScore, Entity, Poll


class Recommender:
    # Graph containing all videos and existing comparisons, used to get the video preferences
    _complete_graph: Graph
    # Dictionary linking a user to its comparison graph, used to get its information gain
    _user_specific_graphs: dict[User, Graph]

    POLL_NAME = "videos"
    poll = Poll.default_poll()

    def __init__(self):
        # build complete graph
        query: QuerySet = ComparisonCriteriaScore.objects
        comparisons = query.all()
        for c in comparisons:
            self._complete_graph.add_edge(c.entity_1, c.entity_2)

        query.filter(
            comparison__poll__name=self.poll.name
        )

        comparisons = query.all()
        for c in comparisons:
            self._complete_graph.add_edge(c.entity_1, c.entity_2)
        query.filter(
            criteria=self.poll.criterias_list[0]
        )

        # comparisons = query.query()
        comparisons = query.all()
        for c in comparisons:
            self._complete_graph.add_edge(c.entity_1, c.entity_2)

    def get_scale_augmenting_videos(self) -> list[Video]:
        pass

    def do_offline_computation(self):
        # for requests => look at ml->inputs
        scale_aug_vids = self.get_scale_augmenting_videos()
        for g in self._user_specific_graphs.values():
            # Will be cached, do at registration
            g.compute_offline_parameters(scale_aug_vids)

    def register_new_user(self, new_user):
        self._user_specific_graphs[new_user] = Graph()

    def register_user_comparison(self, user: User, va: Video, vb: Video):
        self._complete_graph.add_edge(va, vb)
        self._user_specific_graphs[user].add_edge(va, vb)

    def get_first_video_recommendation(self, user: User, nb_video_required: int) -> list[Video]:
        # if user not in array, register it
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
            v.user_pref = max(v.nb_comparison_with.values())/v.comparison_nb
            if v.user_pref > max_vid_pref:
                max_vid_pref = v.user_pref

        for i in range(nb_video_required):
            for v in considered_vids_list:
                act_user_pref = v.user_pref
                if act_user_pref >= (nb_video_required - i)/(nb_video_required + 1) * max_vid_pref:
                    result.append(v)
        return result

    def get_second_video_recommendation(self, user, first_video_id, nb_video_required: int) -> list[Video]:
        # if user not in array, register it
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
                if act_user_pref >= (nb_video_required - i)/(nb_video_required + 1) * max_vid_pref:
                    result.append(v)
        return result
