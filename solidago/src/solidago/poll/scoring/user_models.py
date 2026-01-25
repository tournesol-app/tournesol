from typing import Iterable, TYPE_CHECKING
from numpy.typing import NDArray
from pathlib import Path
from copy import deepcopy

import pandas as pd
import numpy as np
import yaml
import logging

from solidago.poll.entities.entities import Entities, Entity

logger = logging.getLogger(__name__)

from solidago.poll.users import User, Users
from .model import CategoryScores, DirectScores, Multipliers, Parameters, ScoringModel, Translations
from .score import MultiScore, Score


class UserDirectScores(DirectScores):
    name: str="user_directs"
    default_keynames: tuple = ("username", "entity_name", "criterion")

class UserCategoryScores(CategoryScores):
    name: str="user_categories"
    default_keynames: tuple = ("username", "category", "group", "criterion")

class UserParameters(Parameters):
    name: str="user_parameters"
    default_keynames: tuple = ("username", "criterion", "coordinate")

class UserMultipliers(Multipliers):
    name: str="user_multipliers"
    default_keynames: tuple = ("username", "height", "criterion")

class UserTranslations(Translations):
    name: str="user_translations"
    default_keynames: tuple = ("username", "height", "criterion")

class CommonMultipliers(Multipliers):
    name: str="common_multipliers"

class CommonTranslations(Translations):
    name: str="common_translations"


class UserModels:
    table_names: list[str] = [
        "user_directs", "user_categories", "user_parameters",
        "user_multipliers", "user_translations", "common_multipliers", "common_translations"
    ]

    def __init__(self, 
        default_composition: list[tuple[str, dict]] | None = None,
        user_compositions: dict[str, tuple] | None = None,
        user_directs: UserDirectScores | None = None,
        user_categories: UserCategoryScores | None = None,
        user_parameters: UserParameters | None = None,
        user_multipliers: UserMultipliers | None = None,
        user_translations: UserTranslations | None = None,
        common_multipliers: CommonMultipliers | None = None,
        common_translations: CommonTranslations | None = None,
        user_models_dict: dict[str, ScoringModel] | None = None,
    ):
        self.default_composition = default_composition or [("Direct", dict())]
        self.user_compositions = user_compositions or dict()
        self.user_directs = user_directs or UserDirectScores()
        self.user_categories = user_categories or UserCategoryScores()
        self.user_parameters = user_parameters or UserParameters()
        self.user_multipliers = user_multipliers or UserMultipliers()
        self.user_translations = user_translations or UserTranslations()
        self.common_multipliers = common_multipliers or CommonMultipliers()
        self.common_translations = common_translations or CommonTranslations()
        self._cache_users = user_models_dict

    def criteria(self) -> set[str]:
        return set.union(*[getattr(self, name).keys("criterion") for name in self.table_names])
    
    def get_composition(self, user: str | User) -> tuple[str, dict]:
        username = user.name if isinstance(user, User) else user
        if username in self.user_compositions:
            return self.user_compositions[username]
        return deepcopy(self.default_composition)
    
    def to_dict(self) -> dict[str, ScoringModel]:
        if self._cache_users is None:
            self._cache_users = dict()
            usernames = set(self.user_compositions.keys())
            for table_name in self.table_names:
                if table_name.startswith("user_"):
                    usernames |= getattr(self, table_name).keys("username")
            for username in usernames:
                self._cache_users[username] = ScoringModel(
                    self.get_composition(username),
                    self.user_directs[username],
                    self.user_categories[username],
                    self.user_parameters[username],
                    self.user_multipliers[username] | self.common_multipliers,
                    self.user_translations[username] | self.common_translations,
                )
        return self._cache_users

    def __getitem__(self, user: str | User) -> ScoringModel:
        username = user.name if isinstance(user, User) else user
        d = self.to_dict()
        model = d[username] if username in d else ScoringModel(self.get_composition(username))
        assert isinstance(model, ScoringModel)
        return model
    
    def __delitem__(self, user: str | User) -> None:
        username = user.name if isinstance(user, User) else user
        user_tablenames = [n for n in self.table_names if n.startswith("user")]
        for name in user_tablenames:
            del getattr(self, name)[username]
        if username in self.user_compositions:
            del self.user_compositions[username]
        if self._cache_users is not None and username in self._cache_users:
            del self._cache_users[username]
        
    def __setitem__(self, user: str | User, model: ScoringModel) -> None:
        username = user.name if isinstance(user, User) else user
        del self[username]
        for tablename in ("directs", "categories", "parameters"):
            for keys, value in getattr(model, tablename):
                getattr(self, f"user_{tablename}")[username, *keys] = value
        for scaling in ("multipliers", "translations"):
            for keys, value in getattr(model, scaling):
                if keys not in getattr(self, f"common_{scaling}"):
                    getattr(self, f"user_{scaling}")[username, *keys] = value
        if not model.matches_composition(ScoringModel(self.default_composition)):
            self.user_compositions[username] = model.save()
        if self._cache_users is not None:
            self._cache_users[username] = model

    def __call__(self, 
        entities: str | Entity | Entities | slice = slice(None),
        criteria: str | set | slice = slice(None),
        n_sampled_entities_per_user: int | None = None,
        keynames: list[str] | None = None,
    ) -> MultiScore:
        return self.score(entities, criteria, n_sampled_entities_per_user, keynames)
    
    def score(self, 
        entities: str | Entity | Entities | slice = slice(None),
        criteria: str | set | slice = slice(None),
        n_sampled_entities_per_user: int | None = None,
        keynames: list[str] | None = None,
    ) -> MultiScore:
        if keynames is None:
            keynames = ["username"]
            from solidago.poll.entities import Entities
            keynames += ["entity_name"] if isinstance(entities, (Entities, slice)) else list()
            keynames += ["criterion"] if isinstance(criteria, (set, slice)) else list()
        assert "username" in keynames, keynames
        assert "entity_name" in keynames or not isinstance(entities, (Entities, slice)), (keynames, entities)
        assert "criterion" in keynames or not isinstance(criteria, (set, slice)), (keynames, criteria)
        results = MultiScore(keynames)
        username_index = keynames.index("username")
        non_username_keynames = [kn for kn in keynames if kn != "username"]
        for username, model in self:
            assert isinstance(model, ScoringModel)
            for subkeys, score in model(entities, criteria, n_sampled_entities_per_user, non_username_keynames):
                keys = list(subkeys[:username_index]) + [username] + list(subkeys[username_index:])
                results[*keys] = score
        return results

    def __len__(self) -> int:
        if self._cache_users is None:
            try:
                """ Desperate attempt for a fast response """
                return len(set(self.user_directs.init_data["username"]))
            except TypeError:
                return len(self.to_dict())
        return len(self.to_dict())
    
    def __contains__(self, user: str | User) -> bool:
        username = user.name if isinstance(user, User) else user
        return username in self.to_dict()
    
    def __iter__(self) -> Iterable[tuple[str, ScoringModel]]:
        for username, model in self.to_dict().items():
            assert isinstance(username, str) and isinstance(model, ScoringModel)
            yield username, model
            
    def height(self, user: str | User | None = None) -> int:
        username = user.name if isinstance(user, User) else user
        if username is None or username not in self.user_compositions:
            return len(self.default_composition)
        return len(self.user_compositions[username])

    def to_matrices(self, users: Users, entities: Entities, criterion: str) -> tuple[NDArray, NDArray, NDArray]:
        value_matrix = np.full((len(users), len(entities)), np.nan)
        left_matrix = np.full((len(users), len(entities)), np.nan)
        right_matrix = np.full((len(users), len(entities)), np.nan)
        for username, model in self:
            user_index = users.name2index(username)
            for entity_name, score in model(entities, criterion):
                assert isinstance(score, Score)
                entity_index = entities.name2index(entity_name)
                value_matrix[user_index, entity_index] = score.value
                left_matrix[user_index, entity_index] = score.left_unc
                right_matrix[user_index, entity_index] = score.right_unc
        return value_matrix, left_matrix, right_matrix
    
    def common_scale(self, 
        multipliers: Multipliers | None = None, # keynames == ["criterion"]
        translations: Translations | None = None, # keynames == ["criterion"]
        note: str = "scale",
    ) -> "UserModels":
        """ This operation must leave self unchanged """
        height = len(self.default_composition)
        common_multipliers = self.common_multipliers.clone_append(multipliers, height=height)
        common_translations = self.common_translations.clone_append(translations, height=height)

        user_multipliers, user_translations = self.user_multipliers, self.user_translations
        for (user_scales, scales) in zip((user_multipliers, user_translations), (multipliers, translations)):
            if self.user_compositions and scales:
                user_scales = user_scales.deepcopy()
                for username in self.user_compositions:
                    user_scales |= scales.prepend(username=username, height=self.height(username))

        cache_users = None if self._cache_users is None else {
            user: model.scale(multipliers, translations, note=note) 
            for user, model in self._cache_users.items()
        }

        return UserModels(
            self.default_composition + [("Scale", dict(note=note))],
            {u: c + [("Scale", dict(note=note))] for u, c in self.user_compositions.items()},
            self.user_directs, self.user_categories, self.user_parameters,
            user_multipliers, user_translations,
            common_multipliers, common_translations,
            cache_users
        )
    
    def user_scale(self,
        multipliers: Multipliers | None = None, # keynames == ["username", "criterion"]
        translations: Translations | None = None, # keynames == ["username", "criterion"]
        note: str = "scale",        
    ) -> "UserModels":
        """ This operation must leave self unchanged """
        user_multipliers, user_translations = self.user_multipliers, self.user_translations

        if multipliers:
            multipliers = multipliers.reorder("username", "criterion")
            assert set(multipliers.keynames) == {"username", "criterion"}, multipliers.keynames
            user_multipliers = self.user_multipliers.deepcopy()
            for (username, criterion), value in multipliers:
                user_multipliers[username, self.height(username), criterion] = value

        if translations:
            translations = translations.reorder("username", "criterion")
            assert set(translations.keynames) == {"username", "criterion"}, translations.keynames
            user_translations = self.user_translations.deepcopy()
            for (username, criterion), value in translations:
                user_translations[username, self.height(username), criterion] = value

        cache_users = None if self._cache_users is None else {
            user: model.scale(
                multipliers[user] if multipliers else None, 
                translations[user] if translations else None, 
                note=note
            ) for user, model in self._cache_users.items()
        }

        return UserModels(
            self.default_composition + [("Scale", dict(note=note))],
            {u: c + [("Scale", dict(note=note))] for u, c in self.user_compositions.items()},
            self.user_directs, self.user_categories, self.user_parameters,
            user_multipliers, user_translations,
            self.common_multipliers, self.common_translations,
            cache_users
        )
    
    def post_process(self, operation: str = "Squash", **operation_kwargs) -> "UserModels":
        import solidago.poll.scoring.processing as processing
        assert hasattr(processing, operation)

        cache_users = None if self._cache_users is None else {
            user: model.post_process(operation, **operation_kwargs) 
            for user, model in self._cache_users.items()
        }
        
        return UserModels(
            self.default_composition + [(operation, operation_kwargs)],
            {u: c + [(operation, operation_kwargs)] for u, c in self.user_compositions.items()},
            self.user_directs, self.user_categories, self.user_parameters,
            self.user_multipliers, self.user_translations,
            self.common_multipliers, self.common_translations,
            cache_users
        )
    
    @classmethod
    def load(cls, directory: str | Path, filename: str = "user_models.yaml", **kwargs) -> "UserModels":
        assert (Path(directory) / filename).is_file(), f"No user models found in {directory}"
        with open(Path(directory) / filename) as f:
            clsname, kwargs = yaml.safe_load(f)
        import solidago.poll as poll
        assert hasattr(poll, clsname) and issubclass(getattr(poll, clsname), UserModels), clsname
        return getattr(poll, clsname).load_tables(directory, **kwargs)
    
    @classmethod
    def load_tables(cls, directory: str | Path, **kwargs) -> "UserModels":
        def get_kwargs(key):
            return dict(source=f"{key}.csv") | kwargs[key] if key in kwargs else dict()
        return cls(
            kwargs["default_composition"] if "default_composition" in kwargs else None,
            kwargs["user_compositions"] if "user_compositions" in kwargs else dict(),
            UserDirectScores.load(directory, **get_kwargs("user_directs")),
            UserCategoryScores.load(directory, **get_kwargs("user_categories")),
            UserParameters.load(directory, **get_kwargs("user_parameters")),
            UserMultipliers.load(directory, **get_kwargs("user_multipliers")),
            UserTranslations.load(directory, **get_kwargs("user_translations")),
            CommonMultipliers.load(directory, **get_kwargs("common_multipliers")),
            CommonTranslations.load(directory, **get_kwargs("common_translations")),
        )
    
    def save(self, directory: Path | str | None = None, save_instructions: bool = True) -> tuple[str, dict]:
        for table_name in self.table_names:
            self.save_table(directory, table_name)
        return self.save_instructions(directory, save_instructions)
    
    def save_instructions(self, directory: Path | str | None = None, save_instructions: bool = True) -> tuple[str, dict]:
        kwargs = dict(default_composition=self.default_composition)
        if len(self.user_compositions) > 0:
            kwargs["user_compositions"] = self.user_compositions
        if self.user_categories:
            kwargs["user_categories"] = dict(categories_list=self.user_categories.list)
        if self.user_parameters:
            kwargs["user_parameters"] = dict(n_coordinates=self.user_parameters.n_coordinates)
        instructions = type(self).__name__, kwargs
        if directory and save_instructions:
            with open(Path(directory) / "user_models.yaml", "w") as f:
                yaml.safe_dump(instructions, f)
        return instructions
    
    def save_table(self, directory: Path | str | None, table_name: str) -> str | None:
        assert table_name in self.table_names, table_name
        table = getattr(self, table_name)
        if directory and table:
            assert isinstance(table, MultiScore)
            table.save(directory, f"{table_name}.csv")
            return f"{table_name}.csv"
        return None

    def __repr__(self) -> str:
        r = type(self).__name__ + ": " + " < ".join([o for o, _ in self.default_composition])
        return r + "\n\n" + "\n\n".join([
            f"{table_name}\n{repr(getattr(self, table_name))}" 
            for table_name in self.table_names 
            if getattr(self, table_name)
        ])
        
    def has_default_type(self) -> bool:
        return False