from abc import abstractmethod
from datetime import datetime

import numpy as np

from solidago.poll import *
from solidago.poll_functions.parallelized import ParallelizedPollFunction


class PreferenceBias(ParallelizedPollFunction):
    block_parallelization = False

    def __init__(self, time: datetime | str | None = None):
        self.time = datetime.fromisoformat(time) if isinstance(time, str) else time

    def _variables(self, user_models: UserModels) -> list[tuple[str, str]]: # type: ignore
        return [
            (username, criterion) 
            for username in user_models.usernames() 
            for criterion in user_models.criteria()
        ]
    
    def _args(self, variable: tuple[str, str], nonargs, user_models: UserModels) -> Scores: # type: ignore
        username, criterion = variable
        scores = user_models[username](criterion=criterion)
        assert isinstance(scores, Scores)
        return scores
    
    def thread_function(self, scores: Scores, poll: Poll) -> Scores:
        biased_scores = scores * self.multipliers(poll, scores)
        assert isinstance(biased_scores, Scores)
        return biased_scores
    
    def _process_results(self,  # type: ignore
        variables: list[tuple[str, str]], 
        nonargs_list: list, 
        results: list[DirectScores], 
        args_lists: list, 
    ) -> UserModels:
        user_models = UserModels()
        for (username, criterion), scores in zip(variables, results):
            s = scores.add_columns(username=username, criterion=criterion)
            user_models.user_directs = user_models.user_directs | s
        return user_models
            
    @abstractmethod
    def multipliers(self, poll: Poll, scores: Scores) -> Scores:
        raise NotImplemented
    

class WeightPreservingBias(PreferenceBias):
    def thread_function(self, scores: Scores, poll: Poll) -> Scores:
        biased_scores = scores * self.multipliers(poll, scores)
        assert isinstance(biased_scores, Scores)
        s = biased_scores * np.abs(scores.value).sum() / np.abs(biased_scores.value).sum()
        assert isinstance(s, Scores)
        return s
