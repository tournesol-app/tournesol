from abc import abstractmethod
from numpy.typing import NDArray

import numpy as np

from solidago.poll import *
from solidago.functions.threaded import ThreadedPollFunction
from solidago.primitives.time import Date, DateInput


class PreferenceBias(ThreadedPollFunction):
    parallelize: bool = False

    def __init__(self, date: DateInput | None = None, max_workers: int | None = None):
        self.date = None if date is None else Date(date)
        super().__init__(max_workers=max_workers)

    def _variables(self, user_models: UserModels) -> list[tuple[str, str]]: # type: ignore
        return [
            (username, criterion) 
            for username in user_models.usernames() 
            for criterion in user_models.criteria()
        ]
    
    def _args(self, variable: tuple[str, str], nonargs, user_models: UserModels) -> Scores: # type: ignore
        username, criterion = variable
        return user_models[username](criterion=criterion)
    
    def thread_function(self, scores: Scores, **kwargs) -> Scores:
        return scores * self.multipliers(scores, **kwargs)
    
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

    def multipliers(self, scores: Scores, **kwargs) -> Scores:
        v, l, r = self._multipliers(scores, **kwargs)
        return Scores(
            dict(entity_name=scores("entity_name"), value=v, left_unc=l, right_unc=r), 
            columns=["entity_name", "value", "left_unc", "right_unc"],
            keynames=["entity_name"],
        )
    
    @abstractmethod
    def _multipliers(self, 
        scores: Scores, 
        **kwargs
    ) -> tuple[NDArray, NDArray | float, NDArray | float]:
        raise NotImplemented
    

class WeightPreservingBias(PreferenceBias):
    def thread_function(self, scores: Scores, **kwargs) -> Scores:
        biased_scores = scores * self.multipliers(scores, **kwargs)
        return biased_scores * np.abs(scores.value).sum() / np.abs(biased_scores.value).sum()
