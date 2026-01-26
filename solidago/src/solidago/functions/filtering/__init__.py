from copy import deepcopy
from typing import Iterable
from solidago.poll import *


class Filtering:
    def __init__(self,
        users: str | User | Iterable | slice = slice(None),
        entities: str | Entity | Iterable | slice = slice(None),
        criteria: str | Iterable | slice = slice(None),
    ):
        self.users = Filtering.to_set(users)
        self.entities = Filtering.to_set(entities)
        self.criteria = Filtering.to_set(criteria)
    
    def to_set(variables: str | User | Entity | Iterable | slice) -> set[str] | slice:
        if isinstance(variables, (User, Entity)):
            return Filtering.to_set(variables.name)
        if isinstance(variables, str):
            return {variables}
        if isinstance(variables, slice):
            return variables
        assert isinstance(variables, Iterable)
        assert all(isinstance(v, (str, User, Entity)) for v in variables)
        return {v.name if isinstance(v, (User, Entity)) else v for v in variables}
    
    @property
    def all_users(self) -> bool:
        return isinstance(self.users, slice)
    @property
    def all_entities(self) -> bool:
        return isinstance(self.entities, slice)
    @property
    def all_criteria(self) -> bool:
        return isinstance(self.criteria, slice)
    def has_user(self, username) -> bool:
        return self.all_users or username in self.users
    def has_entity(self, entity_name) -> bool:
        return self.all_entities or entity_name in self.entities
    def has_criterion(self, criterion) -> bool:
        return self.all_criteria or criterion in self.criteria

    def __call__(self, poll: Poll) -> Poll:
        return Poll(
            self._get_users(poll.users),
            self._get_entities(poll.entities),
            self._get_vouches(poll.vouches),
            self._get_made_public(poll.made_public),
            self._get_ratings(poll.ratings),
            self._get_comparisons(poll.comparisons),
            self._get_voting_rights(poll.voting_rights),
            self._get_user_models(poll.user_models),
            self._get_global_model(poll.global_model),
        )

    def _get_users(self, users: Users) -> Users:
        return deepcopy(users) if self.all_users else Users([users[name] for name in self.users])
    
    def _get_entities(self, entities: Entities) -> Entities:
        return deepcopy(entities) if self.all_entities else Entities([entities[name] for name in self.entities])
    
    def _get_vouches(self, vouches: Vouches) -> Vouches:
        if self.all_users:
            return deepcopy(vouches)
        filtered_vouches = Vouches()
        for (by, to, kind), value in Vouches:
            if self.has_user(by) and self.has_user(to):
                filtered_vouches[by, to, kind] = value
        return filtered_vouches
    
    def _get_made_public(self, made_public: MadePublic) -> MadePublic:
        if self.all_users and self.all_entities:
            return deepcopy(made_public)
        filtered_made_public = MadePublic()
        for (username, entity_name), value in made_public:
            if self.has_user(username) and self.has_entity(entity_name):
                filtered_made_public[username, entity_name] = value
        return filtered_made_public
    
    def _get_ratings(self, ratings: Ratings) -> Ratings:
        if self.all_users and self.all_entities and self.all_criteria:
            return deepcopy(ratings)
        filtered_ratings = Ratings()
        for (username, criterion, entity_name), value in ratings:
            if self.has_user(username) and self.has_criterion(criterion) and self.has_entity(entity_name):
                filtered_ratings[username, criterion, entity_name] = value
        return filtered_ratings
    
    def _get_comparisons(self, comparisons: Comparisons) -> Comparisons:
        if self.all_users and self.all_entities and self.all_criteria:
            return deepcopy(comparisons)
        filtered_comparisons = Comparisons()
        for (u, c, left, right), value in comparisons.left_right_iter():
            if self.has_user(u) and self.has_criterion(c) and self.has_entity(left) and self.has_entity(right):
                filtered_comparisons[u, c, left, right] = value
        return filtered_comparisons
    
    def _get_voting_rights(self, voting_rights: VotingRights) -> VotingRights:
        if self.all_users and self.all_entities and self.all_criteria:
            return deepcopy(voting_rights)
        filtered_voting_rights = VotingRights()
        for (username, entity_name, criterion), value in voting_rights:
            if self.has_user(username) and self.has_criterion(criterion) and self.has_entity(entity_name):
                filtered_voting_rights[username, entity_name, criterion] = value
        return filtered_voting_rights

    def _get_user_models(self, user_models: UserModels) -> UserModels:
        filtered_user_models = deepcopy(user_models)
        if self.all_users and self.all_entities and self.all_criteria:
            return filtered_user_models
        filtered_user_models.user_directs = MultiScore(["username", "entity_name", "criterion"], name="user_directs")
        for (username, entity_name, criterion), value in user_models.user_directs:
            if self.has_user(username) and self.has_criterion(criterion) and self.has_entity(entity_name):
                filtered_user_models.user_directs[username, entity_name, criterion] = value
        return filtered_user_models
    
    def _get_global_model(self, global_model: ScoringModel) -> ScoringModel:
        filtered_global_model = deepcopy(global_model)
        if self.all_users and self.all_entities and self.all_criteria:
            return filtered_global_model
        filtered_global_model.directs = MultiScore(["entity_name", "criterion"], name="directs")
        for (entity_name, criterion), value in global_model.directs:
            if self.has_criterion(criterion) and self.has_entity(entity_name):
                filtered_global_model.directs[entity_name, criterion] = value
        return filtered_global_model
