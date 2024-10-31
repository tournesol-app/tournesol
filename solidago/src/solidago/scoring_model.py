from abc import abstractmethod
from typing import Callable, Optional, Union, Iterable

import pandas as pd
import numpy as np


class ScoringModel:
    @abstractmethod
    def __call__(
        self, 
        entity_id: int, 
        entity_features: Optional[pd.Series] = None,
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
        
    def scored_entities(self, entities: Optional[pd.DataFrame] = None) -> set[int]:
        raise NotImplementedError

    def iter_entities(self, entities = None) -> Iterable[tuple[int, tuple[float, float, float]]]:
        for entity_id in self.scored_entities(entities):
            if entities is None:
                result = self(entity_id)
            else:
                result = self(entity_id, entities.loc[entity_id])
            if result is not None:
                yield entity_id, result


class DirectScoringModel(ScoringModel):
    def __init__(
        self, 
        dct: Optional[dict[int, tuple[float, float, float]]]=None
    ):
        super().__init__()
        self._dict = dict() if dct is None else dct
    
    def __call__(self, entity_id: int, entity_features=None) -> Optional[tuple[float, float, float]]:
        """ Returns both score and uncertainty
        """
        return self._dict.get(entity_id)
        
    def __getitem__(self, entity_id: int) -> Optional[tuple[float, float, float]]:
        return self(entity_id)
        
    def __setitem__(
        self,
        entity_id: int,
        score_and_uncertainties: Union[tuple[float, float, float], tuple[float, float]]
    ):
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
        return set(entities.index).intersection(self._dict.keys())

    def iter_entities(self, entities=None) -> Iterable[tuple[int, tuple[float, float, float]]]:
        return self._dict.items()

    def __str__(self, indent=""):
        return "{" + f"\n{indent}    " + f",\n{indent}    ".join([
            f"{entity}: {np.round(self[entity][0], 2)}   "
                + f"[-{np.round(self[entity][1], 2)}, "
                + f"+{np.round(self[entity][2], 2)}]"
            for entity in self.scored_entities()
        ]) + f"\n{indent}" + "}"


class ScaledScoringModel(ScoringModel):
    def __init__(
        self, 
        base_model: ScoringModel, 
        multiplicator: float=1.0,
        translation: float=0.0,
        multiplicator_left_uncertainty: float=0.0,
        multiplicator_right_uncertainty: float=0.0,
        translation_left_uncertainty: float=0.0,
        translation_right_uncertainty: float=0.0,
    ):
        """ When base_model is itself a scaled scoring model, 
        the scalings are aggregated, so that the base model is actually
        the scaled scoring model's base model.
        Note that this requires aggregating the uncertainties in a heuristic manner.
        At the core, this is because the uncertainties should grow quadratically
        with the size of the scores. Put differently, because of uncertainties,
        the composition of scaled scoring models is not an internal composition law
        (but it is if uncertainties are not accounted for).        
        """
        if isinstance(base_model, ScaledScoringModel):
            self.base_model = base_model.base_model
            self.multiplicator = multiplicator * base_model.multiplicator
            self.translation = translation + multiplicator * base_model.translation
            self.multiplicator_left_uncertainty = multiplicator_left_uncertainty \
                + multiplicator * base_model.multiplicator_left_uncertainty
            self.multiplicator_right_uncertainty = multiplicator_right_uncertainty \
                + multiplicator * base_model.multiplicator_right_uncertainty
            self.translation_left_uncertainty = translation_left_uncertainty \
                + multiplicator * base_model.translation_left_uncertainty
            self.translation_right_uncertainty = translation_right_uncertainty \
                + multiplicator * base_model.translation_right_uncertainty
        else:
            self.base_model = base_model
            self.multiplicator = multiplicator
            self.translation = translation
            self.multiplicator_left_uncertainty = multiplicator_left_uncertainty
            self.multiplicator_right_uncertainty = multiplicator_right_uncertainty
            self.translation_left_uncertainty = translation_left_uncertainty
            self.translation_right_uncertainty = translation_right_uncertainty
        
    def __call__(self, entity_id, entity_features=None):
        base_output = self.base_model(entity_id, entity_features)
        if base_output is None:
            return None
        return self.scale_score(*base_output)

    def scale_score(
        self, base_score, base_left_unc, base_right_unc
    ) -> tuple[float, float, float]:
        base_left = base_score - base_left_unc
        base_right = base_score + base_right_unc
        
        score = self.multiplicator * base_score + self.translation
        
        left_uncertainty = self.multiplicator * base_left_unc
        left_uncertainty += self.translation_left_uncertainty
        if base_left > 0:
            left_uncertainty += base_left * min(
                self.multiplicator_left_uncertainty, self.multiplicator)
        else:
            left_uncertainty += (- base_left) * self.multiplicator_right_uncertainty
        
        right_uncertainty = self.multiplicator * base_right_unc
        right_uncertainty += self.translation_right_uncertainty
        if base_right > 0:
            right_uncertainty += base_right * self.multiplicator_right_uncertainty
        else:
            right_uncertainty += (- base_right) * min(
                self.multiplicator_left_uncertainty, self.multiplicator)
            
        return score, left_uncertainty, right_uncertainty
        
    def scored_entities(self, entities=None) -> set[int]:
        return self.base_model.scored_entities(entities)

    def _direct_scaling_parameters(self):
        return (self.multiplicator, self.translation, 
            self.multiplicator_left_uncertainty, self.multiplicator_right_uncertainty, 
            self.translation_left_uncertainty, self.translation_right_uncertainty)

    def iter_entities(self, entities=None) -> Iterable[tuple[int, tuple[float, float, float]]]:
        for (entity_id, values) in self.base_model.iter_entities():
            yield (entity_id, self.scale_score(*values))

    def __str__(self, indent=""):
        result = indent + "{\n" 
        result += f"{indent}    multiplicator = {np.round(self.multiplicator, 2)}"
        result += f"   [{np.round(self.multiplicator_left_uncertainty, 2)}, "
        result += f"{np.round(self.multiplicator_right_uncertainty, 2)}]\n{indent}"
        result += f"    translation = {np.round(self.translation, 2)}"
        result += f"   [{np.round(self.translation_left_uncertainty, 2)}, "
        result += f"{np.round(self.translation_right_uncertainty, 2)}]\n{indent}"
        result += "    base_model = " + self.base_model.__str__(f"    {indent}")
        result += "\n" + indent + "}"
        return result

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
    def __init__(self, base_model: ScoringModel, post_process: Callable):
        """ Defines a derived scoring model, based on a base model and a post process
        
        Parameters
        ----------
        base_model: ScoringModel
        post_process: callable
            Must be a monotonous function float -> float
        """
        self.base_model = base_model
        self.post_process = post_process
    
    def __call__(self, entity_id, entity_features=None):
        result = self.base_model(entity_id, entity_features)
        if result is None:
            return None
        return self.apply_post_process(*result)

    def apply_post_process(self, base_score, base_left_unc, base_right_unc):
        score = self.post_process(base_score)
        left = score - self.post_process(base_score - base_left_unc)
        right = self.post_process(base_score + base_right_unc) - score
        if left < 0:
            assert right < 0
            temp = left
            left = - right
            right = - temp
        return score, left, right

    def scored_entities(self, entities) -> set[int]:
        return self.base_model.scored_entities(entities)

    def iter_entities(self, entities=None) -> Iterable[tuple[int, tuple[float, float, float]]]:
        for (entity_id, values) in self.base_model.iter_entities():
            yield (entity_id, self.apply_post_process(*values))
