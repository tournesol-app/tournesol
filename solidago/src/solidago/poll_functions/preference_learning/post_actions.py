from solidago.poll import *
from solidago.poll_functions import ParallelizedPollFunction
from solidago.primitives.datastructure.named_objects import Contains


class PostActions(ParallelizedPollFunction):
    default_action_weights: dict = dict(post=1, repost=1, report=-1)

    def __init__(self, action_weights: dict | None = None):
        super().__init__()
        self.action_weights = action_weights or self.default_action_weights

    def actions(self) -> set[str]:
        return set(self.action_weights.keys())

    def _variables(self, users: Users) -> list[str]: # type: ignore
        return [u.name for u in users]
    
    def _args(self, # type: ignore
        username: str, 
        nonargs, # not used
        entities: Entities, 
        ratings: Ratings
    ) -> tuple[list[tuple[str, int | float]], list[tuple[str, int | float, str]]]: 
        e = entities.filters(authors=Contains(username))
        publications = list(zip(e.names(), e.get_column("date")))
        r = ratings.filters(username=username, criterion=self.actions())
        reactions = list(zip(r.get_column("entity_name"), r.get_column("date"), r.get_column("criterion")))
        return publications, reactions
    
    def thread_function(self, 
        publications: list[tuple[str, int | float]], 
        reactions: list[tuple[str, int | float, str]]
    ) -> Scores:
        scores = Scores(keynames=["entity_name"])
        
        for name, date in publications:
            scores.append(Score(1), entity_name=name, date=date)

        for name, date, action in reactions:
            if date > scores.get(entity_name=name)["date"]:
                scores.append(Score(self.action_weights[action]), entity_name=name, date=date)

        return scores
    
    def _process_results(self,  # type: ignore
        variables: list[str], 
        nonargs_list: list, 
        results: list[Scores],
        args_lists: list[tuple[list[tuple[str, int | float]], list[tuple[str, int | float, str]]]], 
    ) -> UserModels:
        user_models = UserModels()
        for username, scores in zip(variables, results):
            s = scores.add_columns(username=username, criterion="actions")
            user_models.user_directs = user_models.user_directs | s
        return user_models
