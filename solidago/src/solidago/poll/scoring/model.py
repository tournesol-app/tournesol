from typing import TYPE_CHECKING, Union
from numpy.typing import NDArray
from pathlib import Path

import numpy as np
import yaml
import logging
logger = logging.getLogger(__name__)

from solidago.poll import Entity, Entities


from .score import Score, MultiScore

if TYPE_CHECKING:
    from solidago.poll.scoring.base import BaseScoring
    from solidago.poll.scoring.processing import ScoreProcessing


class DirectScores(MultiScore):
    name: str="directs"
    default_keynames: tuple = ("entity_name", "criterion")

class CategoryScores(MultiScore):
    name: str="categories"
    default_keynames: tuple = ("category", "group", "criterion")

    @classmethod
    def value_factory(cls):
        return Score(0, 0, 0)

class Parameters(MultiScore):
    name: str="parameters"
    default_keynames: tuple = ("criterion", "coordinate")

    @classmethod
    def value_factory(cls):
        return Score(0, 0, 0)
    
    def n_coordinates(self, *keys) -> int:
        multiscores = self[*keys]
        assert multiscores.keynames == ("coordinate",)
        coordinates = [int(i) for i in multiscores.keys("coordinate")]
        return max(coordinates) + 1 if coordinates else 0

    def scores_list(self, *keys) -> list[Score]:
        multiscores, coordinate, values = self[*keys], 0, list()
        if not multiscores:
            return list()
        assert multiscores.keynames == ("coordinate",)
        coordinates = [int(i) for i in multiscores.keys("coordinate")]
        n_coordinates = max(coordinates) + 1 if coordinates else 0
        for coordinate in range(n_coordinates):
            values.append(multiscores[str(coordinate)])
        return values

    def values(self, *keys) -> NDArray:
        return np.array([score.value for score in self.scores_list(*keys)])
    
    def lefts(self, *keys) -> NDArray:
        return np.array([score.left_unc for score in self.scores_list(*keys)])
    
    def rights(self, *keys) -> NDArray:
        return np.array([score.right_unc for score in self.scores_list(*keys)])
    
    def maxima(self, *keys) -> NDArray:
        return np.array([score.max for score in self.scores_list(*keys)])
    
    def minima(self, *keys) -> NDArray:
        return np.array([score.min for score in self.scores_list(*keys)])

class Multipliers(MultiScore):
    name: str="multipliers"
    default_keynames: tuple = ("height", "criterion")

    @classmethod
    def value_factory(cls):
        return Score(1, 0, 0)

class Translations(MultiScore):
    name: str="translations"
    default_keynames: tuple = ("height", "criterion")
    
    @classmethod
    def value_factory(cls):
        return Score(0, 0, 0)


class ScoringModel:
    def __init__(self, 
        composition: list | None = None,
        directs: DirectScores | None = None,
        categories: CategoryScores | None = None,
        parameters: Parameters | None = None,
        multipliers: Multipliers | None = None,
        translations: Translations | None = None,
        note: str | None = None,
    ):
        """ The composition of the Tournesol pipeline global model is [
            ("Direct", dict(note="entitywise_qr_quantile")),
            ("Squash", dict(note="squash", score_max=100})),
        ] """
        self.composition = composition or [("Direct", dict() if note is None else dict(note=note))]
        self.directs = directs or DirectScores()
        self.categories = categories or CategoryScores()
        self.parameters = parameters or Parameters()
        self.multipliers = multipliers or Multipliers()
        self.translations = translations or Translations()

    def __call__(self, 
        entities: str | Entity | Entities | slice = slice(None),
        criteria: str | set | slice = slice(None),
        n_sampled_entities: int | None = None,
        keynames: list[str] | None = None,
    ) -> Score | MultiScore:
        """ Assigns a score to an entity, or to multiple entities. Handles sampling. """
        assert entities is not None
        entities = self.sample_entities(entities, criteria, n_sampled_entities)
        assert entities is not None
        score = self.base_score(entities, criteria, keynames)
        for height in range(1, len(self.composition)):
            score = self.score_processing(height)(criteria, score)
        return score

    def base_score(self, 
        entities: str | Entity | Entities | slice = slice(None),
        criteria: str | set | slice = slice(None),
        keynames: list[str] | None = None,
    ) -> Score | MultiScore:
        """ Assigns a score to an entity, or to multiple entities. Handles keynames recovery. """
        entities, criteria, keynames = self._adjust_keynames(entities, criteria, keynames)
        return self.base_scoring()(entities, criteria, keynames)

    def base_scoring(self) -> "BaseScoring":
        import solidago.poll.scoring.base as base
        clsname, kwargs = self.composition[0]
        assert hasattr(base, clsname), f"Invalid base model composition {clsname}"
        return getattr(base, clsname)(self.directs, self.categories, self.parameters, **kwargs)
    
    def score_processing(self, height: int) -> "ScoreProcessing":
        assert isinstance(height, int) and height >= 1, height
        import solidago.poll.scoring.processing as processing
        clsname, kwargs = self.composition[height]
        assert hasattr(processing, clsname), f"Invalid base model composition {clsname}"
        return getattr(processing, clsname)(self.multipliers[height], self.translations[height], **kwargs)

    def criteria(self) -> set[str]:
        return self.directs.keys("criterion") | self.categories.keys("criterion") | set(self.parameters.keys())
    
    def evaluated_entity_names(self, criteria: str | set | slice = slice(None)) -> set[str]:
        if isinstance(criteria, slice):
            return self.directs.keys("entity_name")
        return self.directs.get(criterion=criteria).keys("entity_name")
    
    def sample_entities(self, 
        entities: str | Entity | Entities | slice = slice(None),
        criteria: str | set | slice = slice(None),
        n_sampled_entities: int | None = None,
    ) -> "Entities":
        from solidago.poll.entities import Entities
        if n_sampled_entities is None:
            return entities
        if isinstance(entities, slice):
            entities = Entities(list(self.evaluated_entity_names(criteria)))
        assert isinstance(entities, Entities)
        return entities.sample(n_sampled_entities)
    
    def _adjust_keynames(self,
        entities: str | Entity | Entities | slice = slice(None),
        criteria: str | set | slice = slice(None),
        keynames: list[str] | None = None,
    ) -> tuple[Union["Entity", "Entities", slice], str | set | slice, list[str]]:
        from solidago.poll.entities import Entity, Entities
        if keynames is None:
            keynames = list()
            if isinstance(entities, (set, Entities, slice)):
                keynames.append("entity_name")
            if isinstance(criteria, (set, slice)):
                keynames.append("criterion")
        assert "entity_name" in keynames or isinstance(entities, (str, Entity))
        assert "criterion" in keynames or isinstance(criteria, str)
        entities = entities[{e.name for e in entities}] if isinstance(entities, Entities) else entities
        if "entity_name" in keynames and isinstance(entities, (str, Entity)):
            entities = {entities} if isinstance(str) else Entities([entities])
        if "criterion" in keynames and isinstance(criteria, str):
            criteria = {criteria}
        if isinstance(criteria, slice):
            criteria = self.criteria()
        return entities, criteria, keynames

    def scale(self, 
        multipliers: Multipliers | None = None, 
        translations: Translations | None = None, 
        note: str = "scale",
    ) -> "ScoringModel":
        kwargs = dict(height=len(self.composition))
        multipliers = (self.multipliers | multipliers.detach().prepend(**kwargs)) if multipliers else self.multipliers
        translations = (self.translations | translations.detach().prepend(**kwargs)) if translations else self.translations
        return ScoringModel(
            self.composition + [("Scale", dict(note=note))],
            self.directs, self.categories, self.parameters,
            multipliers, translations
        )
    
    def post_process(self, operation: str = "Squash", **kwargs) -> "ScoringModel":
        import solidago.poll.scoring.processing as processing
        assert hasattr(processing, operation)

        return ScoringModel(
            self.composition + [(operation, kwargs)],
            self.directs, self.categories, self.parameters,
            self.multipliers, self.translations,
        )

    @classmethod
    def load(cls, directory: str | Path | None = None, filename: str = "scoring_model", **kwargs) -> "ScoringModel":
        if not directory:
            return cls(**kwargs)
        filename = filename[:-5] if filename.endswith(".yaml") else filename
        path = Path(directory) / filename
        assert path.is_file(), f"Scoring model failed. File {path} does not exist."
        with open(path) as f:
            clsname, yaml_kwargs = yaml.safe_load(f)
            kwargs |= yaml_kwargs
        import solidago.poll as poll
        assert hasattr(poll, clsname) and issubclass(getattr(poll, clsname), ScoringModel), clsname
        return getattr(poll, clsname).load_tables(directory, filename, **kwargs)
    
    @classmethod
    def load_tables(cls, directory: str | Path, filename: str = "scoring_model", **kwargs) -> "ScoringModel":
        assert "composition" in kwargs
        def get_kwargs(key):
            return dict(source=f"{filename}_{key}.csv") | (kwargs[key] if key in kwargs else dict())
        return cls(
            composition=kwargs["composition"] if "composition" in kwargs else None,
            directs=DirectScores.load(directory, **get_kwargs("directs")),
            categories=CategoryScores.load(directory, **get_kwargs("categories")),
            parameters=Parameters.load(directory, **get_kwargs("parameters")),
            multipliers=Multipliers.load(directory, **get_kwargs("multipliers")),
            translations=Translations.load(directory, **get_kwargs("translations")),
        )

    def save(self, 
        directory: str | None = None, 
        filename: str = "scoring_model", 
        save_instructions: bool = True,
    ) -> tuple[str, dict]:
        """ save must be given a filename_root (typically without extension),
        as multiple csv files may be saved, with a name derived from the filename_root
        (in addition to the yaml description) """
        for table_name in ("directs", "categories", "parameters", "multipliers", "translations"):
            table = getattr(self, table_name)
            if table:
                assert isinstance(table, MultiScore)
                table.save(directory, f"{filename}_{table_name}.csv")
        return self.save_instructions(directory, filename, save_instructions)

    def save_instructions(self, 
        directory: str | None = None, 
        filename: str = "scoring_model", 
        save_instructions: bool = True,
    ) -> tuple[str, dict]:
        kwargs = dict(composition=self.composition)
        if self.categories:
            kwargs["categories"] = dict(categories_list=self.categories.list)
        if self.parameters:
            kwargs["parameters"] = dict(n_coordinates=self.parameters.n_coordinates)
        instructions = type(self).__name__, kwargs
        if directory and save_instructions:
            with open(Path(directory) / f"{filename}.yaml", "w") as f:
                yaml.safe_dump(instructions, f)
        return instructions

    def matches_composition(self, other: "ScoringModel") -> bool:
        if len(self.composition) != len(other.composition):
            return False
        if not self.base_scoring().matches_composition(other.base_scoring()):
            return False
        for height in range(1, len(self.composition)):
            if not self.score_processing(height).matches_composition(other.score_processing(height)):
                return False
        return True
    
    def base_model(self) -> "ScoringModel":
        return ScoringModel([self.composition[0]], self.directs, self.categories, self.parameters)

    def __str__(self) -> str:
        return type(self).__name__ + ": " + " > ".join([operation for operation, _ in self.composition])
    
    def __repr__(self) -> str:
        r = str(self) + "\n"
        r += "\n".join([f"{clsname}({repr(kwargs)[1:-1]})" for clsname, kwargs in self.composition])
        for name in ("directs", "categories", "parameters", "multipliers", "translations"):
            table = getattr(self, name)
            if table:
                r += f"\n\n{name}\n{repr(table)}"
        return r

    def has_default_type(self) -> bool:
        return False
