from typing import Optional, Union, Any, TYPE_CHECKING
from pathlib import Path
from pandas import DataFrame
from math import sqrt

import pandas as pd
import logging
import yaml

logger = logging.getLogger(__name__)

from .score import Score, MultiScore

if TYPE_CHECKING:
    from solidago.poll import Entity, Entities, Comparisons


class Multipliers(MultiScore):
    name: str="multipliers"
    
    def __init__(self, 
        keynames: list[str]=["criterion"], 
        init_data: Optional[Union[Any]]=None,
        parent_tuple: Optional[tuple["Comparisons", tuple, tuple]]=None,
        *args, **kwargs
    ):
        """ We consider the possibility of multidimensional scoring.
        In the context of Tournesol, for instance, the dimensions are the criteria.
        For scientific peer reviewing, it could be the criteria may be
        {'clarity', 'correctness', 'originality', 'rating'}. """
        super().__init__(keynames, init_data, parent_tuple, *args, **kwargs)

    @classmethod
    def value_factory(cls):
        return Score(1, 0, 0)


class Translations(MultiScore):
    name: str="translations"
    
    def __init__(self, 
        keynames: list[str]=["criterion"], 
        init_data: Optional[Union[Any]]=None,
        parent_tuple: Optional[tuple["Comparisons", tuple, tuple]]=None,
        *args, **kwargs
    ):
        """ We consider the possibility of multidimensional scoring.
        In the context of Tournesol, for instance, the dimensions are the criteria.
        For scientific peer reviewing, it could be the criteria may be
        {'clarity', 'correctness', 'originality', 'rating'}. """
        super().__init__(keynames, init_data, parent_tuple, *args, **kwargs)

    @classmethod
    def value_factory(cls):
        return Score(0, 0, 0)


class ScoringModel:
    def __init__(self, 
        composition: Optional[list]=None,
        directs: Optional[MultiScore]=None,
        scales: Optional[MultiScore]=None,
        note: Optional[str]=None,
        *args, **kwargs
    ):
        """ The composition of the Tournesol pipeline global model is [
            ("direct", dict(note="entitywise_qr_quantile")),
            ("squash", dict(note="squash", score_max=100})),
        ] """
        self.composition = composition or [("direct", dict())]
        if self.composition[0][0] == "direct" and isinstance(note, str):
            self.composition[0][1]["note"] = note
        self.directs = MultiScore(["entity_name", "criterion"], name="directs") if directs is None else directs
        self.scales = MultiScore(["height", "kind", "criterion"], name="scales") if scales is None else scales

    def __call__(self, 
        entities: Union[str, "Entity", "Entities", type]=all, 
        criteria: Union[str, set, type]=all,
        n_sampled_entities: Optional[int]=None,
    ) -> Union[Score, MultiScore]:
        return self.score(entities, criteria, n_sampled_entities)
    
    def score(self, 
        entities: Union[str, "Entity", "Entities", type]=all, 
        criteria: Union[str, set, type]=all,
        n_sampled_entities: Optional[int]=None,
    ) -> Union[Score, MultiScore]:
        """ Assigns a score to an entity, or to multiple entities.
        
        Parameters
        ----------
        entities: Union[Entity, Entities]
            
        Returns
        -------
        out: Score or MultiScore
            If entities: Entity with unidimensional scoring, the output is a Score.
            If entities: Entity with multivariate scoring, then out[criterion_name] is a Score.
            If entities: Entities with unidimensional scoring, then out[entity_name] is a Score.
            If entities: Entities with multivariate scoring, then out[entity_name] is a MultiScore.
        """
        from solidago.poll.entities import Entities
        if n_sampled_entities is not None:
            if entities is all:
                entities = Entities(list(self.evaluated_entity_names(criteria)))
            assert isinstance(entities, Entities)
            entities = entities.sample(n_sampled_entities)
        score = self.base_score(entities, criteria)
        for height in range(1, len(self.composition)):
            score = self.score_process(score, height, entities, criteria)
        return score
    
    def base_score(self, 
        entities: Union[str, "Entity", "Entities", type]=all, 
        criteria: Union[str, set, type]=all,
    ) -> Union[Score, MultiScore]:
        from solidago.poll.entities import Entities
        entities = {e.name for e in entities} if isinstance(entities, Entities) else entities
        if self.composition[0][0] == "direct":
            return self.directs[entities, criteria]
        raise ValueError(f"Model composition {self.composition[0]} has invalid base")
    
    def score_process(self, 
        scores: Union[Score, MultiScore], 
        height: int,
        entities: Union[str, "Entity", "Entities", type]=all, 
        criteria: Union[str, set, type]=all,
    ) -> Union[Score, MultiScore]:
        cls, kwargs = self.composition[height]
        if cls == "scale":
            return scores * self.multiplier(height, criteria) + self.translation(height, criteria)
        if cls == "squash":
            def f(x):
                return kwargs["score_max"] * x / sqrt(1 + x**2)
            if isinstance(scores, Score):
                score = scores
                value, extremes = f(score.value), [f(score.max), f(score.min)]
                return Score(value, value - min(extremes), max(extremes) - value)
            assert isinstance(scores, MultiScore)
            return MultiScore(scores.keynames, { c: self.score_process(s, height) for c, s in scores })
        raise ValueError(f"Model composition {self.composition} has invalid height {height}")

    def multiplier(self, height: int, criteria: Union[str, set, type]=all) -> Union[Score, Multipliers]:
        multiplier = self.scales[height, "multiplier", criteria]
        if isinstance(criteria, str):
            assert isinstance(multiplier, Score)
            return Score(1, 0, 0) if multiplier.isnan() else multiplier
        return Multipliers(multiplier.keynames, multiplier)

    def translation(self, height: int, criteria: Union[str, set, type]=all) -> Union[Score, Translations]:
        translation = self.scales[height, "translation", criteria]
        if isinstance(criteria, str):
            assert isinstance(translation, Score)
            return Score(0, 0, 0) if translation.isnan() else translation
        return Translations(translation.keynames, translation)        

    def criteria(self) -> set[str]:
        if self.composition[0][0] == "direct":
            return self.directs.keys("criterion")
        raise ValueError(f"Model composition {self.composition} has invalid base")
    
    def evaluated_entity_names(self, criteria: Union[str, set, type]=all) -> set[str]:
        if self.composition[0][0] == "direct":
            if criteria is all:
                return self.directs.keys("entity_name")
            return self.directs.get(criterion=criteria).keys("entity_name")
        raise ValueError(f"Model composition {self.composition} has invalid base")
    
    def evaluated_entities(self, entities: "Entities", criteria: Union[str, set, type]=all) -> "Entities":
        return entities[self.evaluated_entities(criteria)]
    
    def to_direct(self, entities: "Entities") -> "ScoringModel":
        model = ScoringModel()
        for (entity, criterion), score in self(entities):
            if not score.isnan():
                model[entity, criterion] = score
        return model

    def __setitem__(self, keys: tuple, score: Score) -> None:
        assert isinstance(keys, tuple) and len(keys) == 2
        self.set_direct(*keys, score)

    def set_direct(self, entity: Union[str, "Entity"], criterion: str, score: Score) -> None:
        assert self.composition[0][0] == "direct"
        self.directs[entity, criterion] = score

    def set_scale(self, height: int, kind: str, criterion: str, scale: Score) -> None:
        self.scales[height, kind, criterion] = scale

    def set_multiplier(self, height: int, criterion: str, multiplier: Score) -> None:
        self.set_scale(height, "multiplier", criterion, multiplier)
        
    def set_translation(self, height: int, criterion: str, translation: Score) -> None:
        self.set_scale(height, "translation", criterion, translation)
    
    def scale(self, scales: MultiScore, note: str="scale") -> "ScoringModel":
        assert isinstance(scales, MultiScore)
        return ScoringModel(
            self.composition + [("scale", dict(note=note))],
            self.directs,
            self.scales | scales.prepend(height=len(self.composition)),
        )
    
    def squash(self, score_max: float, note: str="squash") -> "ScoringModel":
        return ScoringModel(
            self.composition + [("squash", dict(score_max=score_max, note=note))],
            self.directs,
            self.scales,
        )

    @classmethod
    def load(cls, directory: Union[str, Path], **kwargs) -> "ScoringModel":
        for name in ("directs", "scales"):
            if name not in kwargs:
                continue
            try:
                filename = f"{directory}/{kwargs[name]['name']}"
                init_data = pd.read_csv(filename, keep_default_na=False)
            except (pd.errors.EmptyDataError, ValueError):
                init_data = None
            kwargs[name] = MultiScore(kwargs[name]["keynames"], init_data)
        return cls(**kwargs)

    def save(self, directory: Optional[str]=None, yaml_dump: bool=False) -> tuple[str, dict]:
        """ save must be given a filename_root (typically without extension),
        as multiple csv files may be saved, with a name derived from the filename_root
        (in addition to the yaml description) """
        for table_name in ("directs", "scales"):
            table = getattr(self, table_name)
            if table:
                table.save(directory, f"{table_name}.csv")
        return self.save_instructions(directory, yaml_dump)

    def save_instructions(self, directory: Optional[str]=None, yaml_dump: bool=False) -> tuple[str, dict]:
        instructions = dict(composition=self.composition)
        for table_name in ("directs", "scales"):
            table = getattr(self, table_name)
            if table:
                instructions[table_name] = { "name": f"{table_name}.csv", "keynames": table.keynames }
        if directory is not None and yaml_dump:
            with open(Path(directory) / "model.yaml", "w") as f:
                yaml.safe_dump((type(self).__name__, instructions), f, indent=4)
        return type(self).__name__, instructions

    def matches_composition(self, composition: list) -> bool:
        if len(self.composition) != len(composition):
            return False
        for height, (cls, kwargs) in enumerate(composition):
            if cls != self.composition[height][0]:
                return False
            if cls == "squash" and cls["score_max"] != self.composition[height][1]["score_max"]:
                return False
        return True
    
    def base_model(self) -> "ScoringModel":
        return ScoringModel([self.composition[0]], self.directs)

    def __str__(self) -> str:
        return type(self).__name__ + ": " + " > ".join([operation for operation, _ in self.composition])
    
    def __repr__(self) -> str:
        r = str(self)
        for name in ("directs", "scales"):
            table = getattr(self, name)
            if table:
                r += f"\n\n{name}\n{repr(table)}"
        return r
