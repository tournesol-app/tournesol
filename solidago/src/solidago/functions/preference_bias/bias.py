from abc import abstractmethod

import numpy as np

from solidago.poll import *
from solidago.functions.parallelized import ParallelizedPollFunction
from solidago.primitives.time import Date, DateInput


class PreferenceBias(ParallelizedPollFunction):
    block_parallelization = False

    def __init__(self, date: DateInput | None = None):
        self.date = None if date is None else Date(date)

    def _variables(self, user_models: UserModels) -> list[tuple[str, str]]: # type: ignore
        return [
            (username, criterion) 
            for username in user_models.usernames() 
            for criterion in user_models.criteria()
        ]
    
    def _args(self, variable: tuple[str, str], nonargs, user_models: UserModels) -> Scores: # type: ignore
        username, criterion = variable
        return user_models[username](criterion=criterion)
    
    def thread_function(self, scores: Scores, poll: Poll) -> Scores:
        return scores * self.multipliers(poll, scores)
    
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
        return biased_scores * np.abs(scores.value).sum() / np.abs(biased_scores.value).sum()
