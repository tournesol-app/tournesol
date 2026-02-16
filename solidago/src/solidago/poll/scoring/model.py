from typing import TYPE_CHECKING, Hashable, Iterable, Union
from numpy.typing import NDArray, DTypeLike
from pathlib import Path

import numpy as np
import yaml
import logging
logger = logging.getLogger(__name__)

from solidago.poll.poll_tables import *


from .score import Score, Scores

if TYPE_CHECKING:
    from solidago.poll.scoring.base import BaseScoring
    from solidago.poll.scoring.processing import ScoreProcessing


class DirectScores(Scores):
    name: str="directs"
    default_keynames: set[str] = {"entity_name", "criterion"}

class CategoryScores(Scores):
    name: str="categories"
    default_keynames: set[str] = {"category", "group", "criterion"}
    default_score: tuple[float, float, float] = 0., 0., 0.

class Parameters(Scores):
    name: str="parameters"
    default_keynames: set[str] = {"criterion", "coordinate"}
    default_score: tuple[float, float, float] = 0., 0., 0.

    def n_coordinates(self, **keys: Hashable) -> int:
        multiscores = self.filters(**keys)
        coordinates = [int(i) for i in multiscores.keys("coordinate")] # type: ignore
        return max(coordinates) + 1 if coordinates else 0
    
    def coordinates(self, **keys: Hashable) -> list[int]:
        return list(range(self.n_coordinates(**keys)))

    def scores_list(self, **keys: Hashable) -> list[Score]:
        multiscores, coordinate, values = self.filters(*keys), 0, list()
        if not multiscores:
            return list()
        coordinates = [int(i) for i in multiscores.keys("coordinate")] # type: ignore
        n_coordinates = max(coordinates) + 1 if coordinates else 0
        for coordinate in range(n_coordinates):
            values.append(multiscores.get("unique", coordinate=coordinate))
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

class Multipliers(Scores):
    name: str="multipliers"
    default_keynames: set[str] = {"height", "criterion"}
    default_score: tuple[float, float, float] = (1., 0., 0.)

class Translations(Scores):
    name: str="translations"
    default_keynames: set[str] = {"height", "criterion"}
    default_score: tuple[float, float, float] = (0., 0., 0.)


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
            ("Linear", dict(note="entitywise_qr_quantile")),
            ("Squash", dict(note="squash", score_max=100})),
        ] """
        self.composition = composition or [("Linear", dict() if note is None else dict(note=note))]
        self.directs = directs or DirectScores()
        self.categories = categories or CategoryScores()
        self.parameters = parameters or Parameters()
        self.multipliers = multipliers or Multipliers()
        self.translations = translations or Translations()

    def __call__(self, 
        entities: Entity | Entities,
        criteria: str | Iterable[str] | None = None,
        n_sampled_entities: int | None = None,
    ) -> Score | Scores:
        """ Assigns a score to an entity, or to multiple entities. Handles sampling. """
        evaluated_entity_names = list(self.evaluated_entity_names(criteria))
        entities = entities if isinstance(entities, Entity) else entities[evaluated_entity_names]
        entities = self.sample_entities(entities, n_sampled_entities)
        criteria = self.criteria() if criteria is None else criteria
        score = self.base_score(entities, criteria)
        for height in range(1, len(self.composition)):
            score = self.score_processing(height)(criteria, score)
        return score

    def base_score(self, entities: Entity | Entities | None = None, criteria: str | Iterable[str] | None = None) -> Score | Scores:
        """ Assigns a score to an entity, or to multiple entities. Handles keynames recovery. """
        criteria = self.criteria() if criteria is None else criteria
        assert self.composition[0] != "Linear" or entities is not None
        entities = Entities(dict(name=list(self.directs.keys("entity_name")))) if entities is None else entities
        return self.base_scoring()(entities, criteria)

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
        multipliers = self.multipliers.filters(height=height)
        translations = self.translations.filters(height=height)
        return getattr(processing, clsname)(multipliers, translations, **kwargs)

    def criteria(self) -> set[str]:
        criteria = self.directs.keys("criterion") | self.categories.keys("criterion") | self.parameters.keys("criterion")
        return {str(c) for c in criteria}
    
    def evaluated_entity_names(self, criteria: str | Iterable[str] | None = None) -> set[Hashable]:
        if criteria is None:
            return self.directs.keys("entity_name")
        c: str | list[Hashable] = criteria if isinstance(criteria, str) else list(criteria)
        return self.directs.filters(criterion=c).keys("entity_name")
    
    def sample_entities(self, entities: Entity | Entities, n_sampled_entities: int | None = None) -> Entity | Entities:
        return entities if isinstance(entities, Entity) else entities.sample(n_sampled_entities)

    def scale(self, 
        multipliers: Multipliers | None = None, 
        translations: Translations | None = None, 
        note: str = "scale",
    ) -> "ScoringModel":
        height = len(self.composition)
        multipliers = (self.multipliers | multipliers.add_keys(height=height)) if multipliers else self.multipliers
        translations = (self.translations | translations.add_keys(height=height)) if translations else self.translations
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
            directs=DirectScores.load(directory, **get_kwargs("directs")), # type: ignore
            categories=CategoryScores.load(directory, **get_kwargs("categories")), # type: ignore
            parameters=Parameters.load(directory, **get_kwargs("parameters")), # type: ignore
            multipliers=Multipliers.load(directory, **get_kwargs("multipliers")), # type: ignore
            translations=Translations.load(directory, **get_kwargs("translations")), # type: ignore
        )

    def save(self, 
        directory: str | Path | None = None, 
        filename: str = "scoring_model", 
        save_instructions: bool = True,
    ) -> tuple[str, dict[str, Any]]:
        """ save must be given a filename_root (typically without extension),
        as multiple csv files may be saved, with a name derived from the filename_root
        (in addition to the yaml description) """
        for table_name in ("directs", "categories", "parameters", "multipliers", "translations"):
            table = getattr(self, table_name)
            if table:
                assert isinstance(table, Scores)
                table.save(directory, f"{filename}_{table_name}.csv")
        return self.save_instructions(directory, filename, save_instructions)

    def save_instructions(self, 
        directory: str | Path | None = None, 
        filename: str = "scoring_model", 
        save_instructions: bool = True,
    ) -> tuple[str, dict[str, Any]]:
        kwargs: dict[str, Any] = dict(composition=self.composition)
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
