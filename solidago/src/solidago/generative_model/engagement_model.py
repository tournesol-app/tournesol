from abc import ABC, abstractmethod

import pandas as pd
import numpy as np

from solidago.privacy_settings import PrivacySettings
from solidago.judgments import Judgments, DataFrameJudgments


class EngagementModel(ABC):
    @abstractmethod
    def __call__(
        self, 
        users: pd.DataFrame, 
        entities: pd.DataFrame
    ) -> tuple[PrivacySettings, Judgments]:
        """ Assigns a score to each entity, by each user
        
        Parameters
        ----------
        users: DataFrame
            Must have an index column `user_id`. May have others.
        entities: DataFrame with columns
            * `entity_id`: int
            * And maybe more
        
        Returns
        -------
        privacy: PrivacySettings
            privacy[user][entity] may be True (private), False (public) or None (undefined).
        judgments: Judgments
            judgments[user]["comparisons"] yields the user's comparisons
            judgments[user]["assessments"] yields the user's assessments
        """
        raise NotImplementedError

    def __str__(self):
        return type(self).__name__

    def to_json(self):
        return (type(self).__name__, )
        
                
class SimpleEngagementModel(EngagementModel):
    def __init__(
        self, 
        p_per_criterion: dict[str, float] = {"0": 1.0}, 
        p_private: float = 0.2
    ):
        self.p_per_criterion = p_per_criterion
        self.p_private = p_private

    def __call__(
        self, 
        users: pd.DataFrame, 
        entities: pd.DataFrame
    ) -> tuple[PrivacySettings, DataFrameJudgments]:
        """ Assigns a score to each entity, by each user
        Parameters
        ----------
        users: DataFrame with columns
            * `user_id`: int
            * `n_comparisons`: float
            * `n_comparisons_per_entity`: float
        entities: DataFrame with columns
            * `entity_id`: int
        
        Returns
        -------
        privacy: PrivacySettings
            privacy[user][entity] may be True (private), False (public) or None (undefined).
        judgments: DataFrameJudgments
            judgments[user]["comparisons"] yields the user's comparisons
            judgments[user]["assessments"] yields the user's assessments
        """
        comparison_list = list()
        privacy = PrivacySettings()
        
        for user, row in users.iterrows():
            n_compared_entities = 2 * row["n_comparisons"]
            n_compared_entities /= row["n_comparisons_per_entity"]
            compared = list()
            for entity, _ in entities.iterrows():
                if np.random.random() <= n_compared_entities / len(entities):
                    compared.append(entity)
            if len(compared) <= 1:
                continue
            p_compare_ab = 2 * row["n_comparisons"] / len(compared)  / (len(compared) - 1)
            for a_index, a in enumerate(compared):
                privacy[user, a] = (np.random.random() <= self.p_private)
                for b in compared[a_index + 1:]:
                    if np.random.random() >= p_compare_ab:
                        continue
                    for criterion in self.p_per_criterion:
                        if np.random.random() <= self.p_per_criterion[criterion]:
                            if np.random.random() <= 0.5:
                                comparison_list.append((user, criterion, a, b))
                            else:
                                comparison_list.append((user, criterion, b, a))
        
        c = list(zip(*comparison_list))
        return privacy, DataFrameJudgments(pd.DataFrame(dict(
            user_id=c[0], criteria=c[1], entity_a=c[2], entity_b=c[3])))

    def __str__(self):
        properties = f"p_per_criterion={self.p_per_criterion}, p_private={self.p_private}"
        return f"SimpleEngagementModel({properties})"

    def to_json(self):
        return type(self).__name__, dict(
            p_per_criterion=self.p_per_criterion, 
            p_private=self.p_private
        )
        
