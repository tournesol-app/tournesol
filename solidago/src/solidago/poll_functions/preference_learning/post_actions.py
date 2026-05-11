from solidago.poll import *
from solidago.poll_functions import ParallelizedPollFunction
from solidago.primitives.datastructure.named_objects import Contains


class PostActions(ParallelizedPollFunction):
    default_action_weights: dict = dict(post=1, repost=1, report=-1)

    def __init__(self, action_weights: dict | None = None):
        """ 
        Parameters
        ---------
        criterion: str
            Name of the criterion associated to the learned scoring model
        """
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
    ) -> tuple[
        list[tuple[str, int | float, int | float]], # publications, with name, date, lifetime
        list[tuple[str, int | float, int | float, str]] # reactions, with name, date, lifetime, criterion
    ]: 
        e = entities.filters(authors=Contains(username))
        publications = list(zip(e.names(), e("date"), e("lifetime")))
        r = ratings.filters(username=username, criterion=self.actions())
        reactions = list(zip(r("entity_name"), r("date"), r("lifetime"), r("criterion")))
        return publications, reactions
    
    def thread_function(self, 
        publications: list[tuple[str, int | float, int | float]], 
        reactions: list[tuple[str, int | float, int | float, str]],
    ) -> Scores:
        scores = Scores(keynames=["entity_name", "criterion"])
        
        for name, date, lifetime in publications:
            scores.append(Score(1), entity_name=name, criterion="post", date=date, lifetime=lifetime)

        for name, date, lifetime, action in reactions:
            if date > scores.get(entity_name=name)["date"]:
                score = Score(self.action_weights[action])
                scores.append(score, entity_name=name, date=date, lifetime=lifetime, criterion=action)

        return scores
    
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
