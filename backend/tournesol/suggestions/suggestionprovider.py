from django.db.models import Q, QuerySet

from core.models import User
from tournesol.models import ComparisonCriteriaScore, Entity, Poll
from tournesol.suggestions.graph import Graph
from tournesol.suggestions.suggested_user import SuggestedUser as RecommendationUser
from tournesol.suggestions.suggested_video import SuggestedVideo


class SuggestionProvider:
    """
    An interface class to ask for suggestions of videos to compare
    """
    # Entity to specific video structure dictionary
    _entity_to_video: dict[str, SuggestedVideo]
    _comparison_reference_video: SuggestedVideo
    # Graph containing all videos and existing comparisons, used to get the video preferences
    _complete_graph: Graph
    # Dictionary linking a user to its comparison graph, used to get its information gain
    _user_specific_graphs: dict[int, Graph]

    def __init__(self, actual_poll: Poll):
        """
        Function used to initialize the class
        It must not be called before the DB is ready, as it will call it while constructing the
        complete graph
        """
        self._comparison_reference_video = SuggestedVideo(None)
        self._entity_to_video = {}
        self._user_specific_graphs = {}
        self.poll = actual_poll
        self.criteria = self.poll.criterias_list[0]
        # build complete graph
        comparison_queryset: QuerySet = ComparisonCriteriaScore.objects \
            .filter(comparison__poll__name=self.poll.name) \
            .filter(criteria=self.criteria)
        self._complete_graph = Graph(None, self.poll, self.criteria)

        for c in comparison_queryset:
            # Checks if each compared Entity has already been translated to a SuggestedVideo object
            # and translates it otherwise
            if c.comparison.entity_1.uid not in self._entity_to_video.keys():
                self._entity_to_video[c.comparison.entity_1.uid] = SuggestedVideo(
                    self._comparison_reference_video, from_entity=c.comparison.entity_1
                )

                self._complete_graph.add_node(
                    self._entity_to_video[c.comparison.entity_1.uid]
                )

            if c.comparison.entity_2.uid not in self._entity_to_video.keys():
                self._entity_to_video[c.comparison.entity_2.uid] = SuggestedVideo(
                    self._comparison_reference_video, from_entity=c.comparison.entity_2
                )

                self._complete_graph.add_node(
                    self._entity_to_video[c.comparison.entity_2.uid]
                )

            self._complete_graph.add_edge(
                self._entity_to_video[c.comparison.entity_1.uid],
                self._entity_to_video[c.comparison.entity_2.uid],
            )

        # create required user graphs (none at first in fact)

    def _get_user_comparability_augmenting_videos(self) -> list[SuggestedVideo]:
        """"
        Function called to get the videos to recommend while the scale and translation
        uncertainties of the user are not high enough
        """
        # I want all entities from the current poll compared by supertrusted user
        # todo create alias to properly detect supertrusted ?
        req_entities = Entity.objects \
            .filter(Q(comparisons_entity_1__poll__name=self.poll.name) |
                    Q(comparisons_entity_2__poll__name=self.poll.name))\
            .filter(Q(comparisons_entity_1__user__is_staff=True) |
                    Q(comparisons_entity_2__user__is_staff=True))\
            .distinct()

        return list(map(lambda entity: self._entity_to_video[entity.uid], req_entities))

    def _get_user_rate_later_video_list(self, user: User) -> list[SuggestedVideo]:
        """
        Function to get the list of videos of the user's rate later list
        """
        req_entities = Entity.objects \
            .filter(type=self.poll.name) \
            .filter(videoratelater__user=user)
        return list(map(lambda entity: self._entity_to_video[entity.uid], req_entities))

    def do_offline_computation(self):
        """
        Function to call regularly to keep the variables useful for the suggestions up to date
        with the collected information
        """
        # for requests => look at ml->inputs
        scale_aug_videos = self._get_user_comparability_augmenting_videos()
        for g in self._user_specific_graphs.values():
            # Will be cached, do at registration
            g.compute_offline_parameters(scale_aug_videos)

    def register_new_user(self, new_user: User):
        """
        Function used to register a new user wanting suggestions, it thus initializes its
        comparison graph
        """
        recommendation_user = RecommendationUser(
            self._entity_to_video, new_user, self.criteria, self.poll
        )
        self._user_specific_graphs[new_user.id] = Graph(
            local_user=recommendation_user,
            local_poll=self.poll,
            local_criteria=self.criteria,
        )
        # build user graph
        query: QuerySet = (
            ComparisonCriteriaScore.objects
                                   .filter(comparison__poll__name=self.poll.name)
                                   .filter(criteria=self.criteria)
                                   .filter(comparison__user__email=new_user.email)
        )
        for c in query:
            va = self._entity_to_video[c.comparison.entity_1.uid]
            vb = self._entity_to_video[c.comparison.entity_2.uid]
            self._user_specific_graphs[new_user.id].add_edge(va, vb)

    def register_user_comparison(self, user: User, va: SuggestedVideo, vb: SuggestedVideo):
        """
        Function used to register a comparison submitted by the user, to keep the complete graph
        up to date
        """
        self._complete_graph.add_edge(va, vb)
        if user.id in self._user_specific_graphs.keys():
            self._user_specific_graphs[user.id].add_edge(va, vb)

    def get_first_video_recommendation(
            self,
            user: User,
            nb_video_required: int
    ) -> list[SuggestedVideo]:
        """
        Function used to get the first video recommendation for the requested user and returning
        nb_video_required videos
        """
        # Lazily load the user graph
        if user.id not in self._user_specific_graphs.keys():
            self.register_new_user(user)
        result = []

        # Give the first video id to the graph so the sorting will take that into account
        user_graph = self._user_specific_graphs[user.id]
        user_graph.compute_offline_parameters(self._get_user_comparability_augmenting_videos())
        self._comparison_reference_video.uid = ""
        user_graph.prepare_for_sorting()

        # Prepare the set of videos to sort, taking the videos present in the graph
        # and append the ones that are not yet compared by the user
        considered_vid_list = self._prepare_video_list(user)

        max_vid_pref = 0
        # Todo : take into account the rate later list / already seen videos ?
        for v in considered_vid_list:
            v.user_pref = max(v.nb_comparison_with.values()) / v.comparison_nb
            if v.user_pref > max_vid_pref:
                max_vid_pref = v.user_pref

        for i in range(nb_video_required):
            act_preference_goal = (nb_video_required - i) / (nb_video_required + 1) * max_vid_pref
            for v in considered_vid_list:
                act_user_pref = v.user_pref
                if act_user_pref >= act_preference_goal and v not in result:
                    result.append(v)
                    break
        result.reverse()
        return result

    def get_second_video_recommendation(
            self,
            user: User,
            first_video_id: str,
            nb_video_required: int
    ) -> list[SuggestedVideo]:
        """
        Function used to get the first video recommendation for the requested user, optimizing
        comparison with respect to first_video and returning nb_video_required videos
        """
        # Lazily load the user graphs
        if user.id not in self._user_specific_graphs.keys():
            self.register_new_user(user)
        result = []

        # Give the first video id to the graph so the sorting will take that into account
        user_graph = self._user_specific_graphs[user.id]
        user_graph.compute_offline_parameters(self._get_user_comparability_augmenting_videos())
        self._comparison_reference_video.uid = first_video_id
        user_graph.prepare_for_sorting(first_video_id)

        # Prepare the set of videos to sort, taking the videos present in the graph and append
        # the ones that are not yet compared by the user
        considered_vid_list = self._prepare_video_list(user)

        max_vid_pref = 0
        for v in considered_vid_list:
            v.user_pref = v.nb_comparison_with[first_video_id] / v.comparison_nb
            if v.user_pref > max_vid_pref:
                max_vid_pref = v.user_pref

        for i in range(nb_video_required):
            for v in considered_vid_list:
                act_user_pref = v.user_pref
                act_min_ratio = (nb_video_required - i) / (nb_video_required + 1)
                if (
                        act_user_pref >= act_min_ratio * max_vid_pref
                        and v.uid != first_video_id
                        and v not in result
                ):
                    result.append(v)
                    break
        result.reverse()
        return result

    def _prepare_video_list(self, user: User):
        """
        Function used in the video recommendations, to prepare the set of videos to choose the
        recommendation from
        """
        # Prepare the set of videos to sort, taking the videos present in the graph and append
        # the ones that are not yet compared by the user
        considered_vid = set(self._user_specific_graphs[user.id].nodes)
        tmp = set(self._complete_graph.nodes.copy())
        tmp = tmp.difference(considered_vid)

        considered_vid.update(tmp)
        considered_vid_list = list(considered_vid)
        considered_vid_list.sort(reverse=True)
        return considered_vid_list
