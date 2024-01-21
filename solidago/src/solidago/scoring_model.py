from abc import ABC, abstractmethod
from typing import Optional

import pandas as pd
import numpy as np


class ScoringModel:
    @abstractmethod
    def __call__(
        self, 
        entity_id: int, 
        entity_features: pd.Series
    ) -> Optional[tuple[float, float, float]]:
        """ Assigns a score to an entity
        
        Parameters
        ----------
        entity_id: int
        entity_features: Series
            features of the entity
            
        Returns
        -------
        out: (score, left_uncertainty, right_uncertainty) or None
        """
        raise NotImplementedError
        
    def scored_entities(self, entities) -> set[int]:
        """ If not None, then the scoring model only scores a subset of entities. """
        return set(range(len(entities)))


class DirectScoringModel(ScoringModel):
    def __init__(
        self, 
        dct: Optional[dict[int, tuple[float, float, float]]]=None
    ):
        super().__init__()
        self._dict = dict() if dct is None else dct
    
    def __call__(self, entity_id: int, entity_features=None) -> Optional[float]:
        """ Returns both score and uncertainty
        """
        if entity_id not in self._dict:
            return None
        return self._dict[entity_id]
        
    def __getitem__(self, entity_id: int) -> Optional[tuple[float, float]]:
        return self(entity_id)
        
    def __setitem__(self, entity_id: int, score_and_uncertainties: tuple[float, float, float]):
        if len(score_and_uncertainties) == 2:
            score_and_uncertainties = (
                score_and_uncertainties[0], 
                score_and_uncertainties[1], 
                score_and_uncertainties[1]
            )
        self._dict[entity_id] = score_and_uncertainties

    def scored_entities(self, entities=None) -> set[int]:
        if entities is None:
            return set(self._dict.keys())
        return set(entities.index).intersection(set(self._dict.keys()))

    def __str__(self):
        return "{\n    " + ",\n    ".join([
            f"{entity}: {np.round(self[entity][0], 2)}   "
                + f"[-{np.round(self[entity][1], 2)}, "
                + f"+{np.round(self[entity][2], 2)}]"
            for entity in self.scored_entities()
        ]) + "\n}"

    def get_scaling_parameters(self):
        return 1, 0, 0, 0, 0, 0


class ScaledScoringModel(ScoringModel):
    def __init__(
        self, 
        base_model: ScoringModel, 
        multiplicator: float=1, 
        translation: float=0,
        multiplicator_left_uncertainty: float=0, 
        multiplicator_right_uncertainty: float=0, 
        translation_left_uncertainty: float=0,
        translation_right_uncertainty: float=0
    ):
        self.base_model = base_model
        self.multiplicator = multiplicator
        self.translation = translation
        self.multiplicator_left_uncertainty = multiplicator_left_uncertainty
        self.multiplicator_right_uncertainty = multiplicator_right_uncertainty
        self.translation_left_uncertainty = translation_left_uncertainty
        self.translation_right_uncertainty = translation_right_uncertainty
        
    def __call__(self, entity_id, entity_features):
        base_output = self.base_model(entity_id, entity_features)
        if base_output is None:
            return None
        
        base_score, base_left, base_right = base_output
        score = self.multiplicator * base_score + self.translation
        
        left = self.multiplicator * base_left
        left += np.abs(score) * self.multiplicator_left_uncertainty
        left += self.translation_left_uncertainty
        
        right = self.multiplicator * base_right
        right += np.abs(score) * self.multiplicator_right_uncertainty
        right += self.translation_right_uncertainty
        
        return score, left, right
        
    def scored_entities(self, entities=None) -> set[int]:
        return self.base_model.scored_entities(entities)

    def _direct_scaling_parameters(self):
        return (self.multiplicator, self.translation, 
            self.multiplicator_left_uncertainty, self.multiplicator_right_uncertainty, 
            self.translation_left_uncertainty, self.translation_right_uncertainty)

    def get_scaling_parameters(self):
        model, parameters = self, list()
        while hasattr(model, "base_model"):
            model = model.base_model
            parameters.append(model._direct_scaling_parameters())
        return ScaledScoringModel.compose_scaling_parameters(parameters)

    @classmethod
    def compose_scaling_parameters(parameters):
        result = 1, 0, 0, 0, 0, 0
        for m2, t2, m2_left, m2_right, t2_left, t2_right in parameters:
            m1, t1, m1_left, m1_right, t1_left, t1_right = result
            result[0] = m1 * m2
            result[1] = t2 * m1 + t1
            result[2] = m1_left  * m2 + m2_left  * m1
            result[3] = m1_right * m2 + m2_right * m1
            result[4] = t2_left  * m1 + t1_left
            result[5] = t2_right * m1 + t1_right
        return result


class PostProcessedScoringModel(ScoringModel):
    def __init__(self, base_model: ScoringModel, post_process: callable):
        """ Defines a derived scoring model, based on a base model and a post process
        
        Parameters
        ----------
        base_model: ScoringModel
        post_process: callable
            Must be a monotonous function float -> float
        """
        self.base_model = base_model
        self.post_process = post_process
    
    def __call__(self, entity_id, entity_features):
        base_score, base_left, base_right = self.base_model(entity_id, entity_features)
        score = self.post_process(base_score)
        left = self.post_process(base_score - base_left) - score
        right = self.post_process(base_score - base_right) - score
        if left < 0:
            assert right < 0
            temp = left
            left = - right
            right = - temp
        return score, left, right
        
    def scored_entities(self) -> set[int]:
        return self.base_model.scored_entities()

    def get_scaling_parameters(self):
        return self.base_model.get_scaling_parameters()
