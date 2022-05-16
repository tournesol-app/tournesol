from django.db.models import QuerySet

from core.models import User
from recommendation.recomended_user import User as RecommendationUser
from recommendation.graph import Graph
from recommendation.video import Video
from tournesol.models import ComparisonCriteriaScore, Entity, Poll, Comparison


class Recommender:
    # Entity to specific video structure dictionary
    _entity_to_video: dict[Entity, Video] = {}
    _comparison_reference_video: Video = Video(None)
    # Graph containing all videos and existing comparisons, used to get the video preferences
    _complete_graph: Graph
    # Dictionary linking a user to its comparison graph, used to get its information gain
    _user_specific_graphs: dict[User, Graph] = {}

    def __init__(self):

        self.poll = Poll.default_poll()
        self.criteria = self.poll.criterias_list[0]
        # build complete graph
        query: QuerySet = ComparisonCriteriaScore.objects.filter(
            comparison__poll__name=self.poll.name
        ).filter(
            criteria=self.criteria
        )
        self._complete_graph = Graph(local_user=None, local_poll=self.poll, local_criteria=self.criteria)

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

    def get_user_comparability_augmenting_videos(self) -> list[Video]:
        # I want all entities from the current poll compared by supertrusted user
        req_entities = Entity.objects \
            .filter(comparison__poll__name=self.poll.name) \
            .filter(comparison__user__is_staff=True)  # todo create alias to properly detect supertrusted ?
        return list(map(lambda entity: self._entity_to_video[entity], req_entities))

    def get_user_rate_later_video_list(self, user: User) -> list[Video]:
        req_entities = Entity.objects \
            .filter(type=self.poll.name) \
            .filter(videoratelater__user__email=user.email)
        return list(map(lambda entity: self._entity_to_video[entity], req_entities))

    def do_offline_computation(self):
        # for requests => look at ml->inputs
        scale_aug_vids = self.get_user_comparability_augmenting_videos()
        for g in self._user_specific_graphs.values():
            # Will be cached, do at registration
            g.compute_offline_parameters(scale_aug_vids)

    def register_new_user(self, new_user):
        recommendation_user = RecommendationUser(self._entity_to_video, new_user, self.criteria, self.poll)
        self._user_specific_graphs[new_user] = Graph(local_user=recommendation_user, local_poll=self.poll,
                                                     local_criteria=self.criteria)
        # build user graph
        query: QuerySet = ComparisonCriteriaScore.objects.filter(
            comparison__poll__name=self.poll.name
        ).filter(
            criteria=self.criteria
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

        # Give the first video id to the graph so the sorting will take that into account
        self._user_specific_graphs[user].prepare_for_sorting()

        # Prepare the set of videos to sort, taking the videos present in the graph and append the ones that are not yet
        # compared by the user
        considered_vids_list = self._prepare_video_list(user)

        max_vid_pref = 0
        # Todo : take into account the rate later list / already seen videos ?
        for v in considered_vids_list:
            v.user_pref = max(v.nb_comparison_with.values()) / v.comparison_nb
            if v.user_pref > max_vid_pref:
                max_vid_pref = v.user_pref

        for i in range(nb_video_required):
            for v in considered_vids_list:
                act_user_pref = v.user_pref
                if act_user_pref >= (nb_video_required - i) / (
                        nb_video_required + 1) * max_vid_pref and v not in result:
                    result.append(v)
                    break
        return result

    def get_second_video_recommendation(self, user, first_video_id, nb_video_required: int) -> list[Video]:
        # Lazily load the user graphs
        if user not in self._user_specific_graphs.keys():
            self.register_new_user(user)
        result = []

        # Give the first video id to the graph so the sorting will take that into account
        self._user_specific_graphs[user].prepare_for_sorting(first_video_id)

        # Prepare the set of videos to sort, taking the videos present in the graph and append the ones that are not yet
        # compared by the user
        considered_vids_list = self._prepare_video_list(user)

        max_vid_pref = 0
        for v in considered_vids_list:
            v.user_pref = v.nb_comparison_with[first_video_id] / v.comparison_nb
            if v.user_pref > max_vid_pref:
                max_vid_pref = v.user_pref

        for i in range(nb_video_required):
            for v in considered_vids_list:
                act_user_pref = v.user_pref
                if act_user_pref >= (nb_video_required - i) / (
                        nb_video_required + 1) * max_vid_pref and v.uid != first_video_id and v not in result:
                    result.append(v)
                    break
        return result

    def _prepare_video_list(self, user):
        # Prepare the set of videos to sort, taking the videos present in the graph and append the ones that are not yet
        # compared by the user
        considered_vids = set(self._user_specific_graphs[user].nodes)
        tmp = set(self._complete_graph.nodes.copy())
        tmp = tmp.difference(considered_vids)

        considered_vids.update(tmp)
        considered_vids_list = list(considered_vids)
        considered_vids_list.sort(reverse=True)
        return considered_vids_list
