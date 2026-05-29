from solidago.poll import *
from solidago.functions.threaded import ThreadedPollFunction
from solidago.primitives.datastructure.filtered_table import SelectLast
from solidago.primitives.datastructure.named_objects import Contains


class PostActions(ThreadedPollFunction):
    default_action_weights: dict = dict(repost=1, report=-1)
    default_default_lifetime: int | float = 3600 * 24 * 3

    def __init__(self, 
        action_weights: dict | None = None,
        default_lifetime: int | float | None = None,
        max_workers: int | None = None,
    ):
        """ 
        Parameters
        ---------
        criterion: str
            Name of the criterion associated to the learned scoring model
        """
        super().__init__(max_workers)
        self.action_weights = action_weights or self.default_action_weights
        self.default_lifetime = self.default_default_lifetime if default_lifetime is None else default_lifetime

    def actions(self) -> set[str]:
        return set(self.action_weights.keys())

    def _variables(self, users: Users) -> list[str]: # type: ignore
        return [u.name for u in users]
    
    def _args(self, # type: ignore
        variable: str, 
        nonargs, # not used
        entities: Entities, 
        ratings: Ratings
    ) -> tuple[
        list[tuple[str, float, int | float]], # publications, with name, timestamp, lifetime
        list[tuple[str, float, int | float, str]] # reactions, with name, timestamp, lifetime, criterion
    ]:
        username = variable
        publications = list()
        if "authors" in entities.columns:
            e = entities.filters(authors=Contains(username))
            publications = list(zip(
                e.names(), 
                e("timestamp", 0), 
                e("lifetime", self.default_lifetime)
            ))
        r = ratings.filters(username=username, criterion=self.actions())
        reactions = list(zip(
            r("entity_name"), 
            r("timestamp", 0), 
            r("lifetime", self.default_lifetime), 
            r("criterion")
        ))
        return publications, reactions
    
    def thread_function(self, 
        publications: list[tuple[str, float, int | float]], 
        reactions: list[tuple[str, float, int | float, str]],
    ) -> Scores:
        scores = Scores(
            publications,
            columns=["entity_name", "timestamp", "lifetime"],
            keynames=["entity_name"],
            default_select=SelectLast("timestamp"),
        ).add_columns(value=1, left_unc=0, right_unc=0, criterion="post")
        scores.keynames.append("criterion")

        latest = dict()
        for name, timestamp, lifetime, action in reactions:
            if "post" in scores.filters(entity_name=name)("criterion"):
                continue
            if name not in latest or timestamp > latest[name][1]:
                latest[name] = name, timestamp, lifetime, action, self.action_weights[action]

        return scores | Scores(
            latest.values(),
            columns=["entity_name", "timestamp", "lifetime", "criterion", "value"],
            keynames=["entity_name", "criterion"],
        ).add_columns(left_unc=0, right_unc=0)
    
    def _process_results(self,  # type: ignore
        variables: list[str], 
        nonargs_list: list, 
        results: list[Scores],
        args_lists: list, 
    ) -> UserModels:
        user_models = UserModels()
        for username, scores in zip(variables, results):
            s = scores.add_columns(username=username)
            user_models.user_directs = user_models.user_directs | s
        return user_models
