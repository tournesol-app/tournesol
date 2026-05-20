from typing import Any, Hashable
from numpy.typing import DTypeLike, NDArray

import numpy as np, pandas as pd

from solidago.primitives.datastructure import Row, FilteredTable
from solidago.primitives.datastructure.filtered_table import Select, SelectLast
from solidago.primitives.datastructure.named_objects import NamedObject, NamedObjects


class User(NamedObject):
    pass

class Users(NamedObjects[User]):
    name: str = "users"
    
    def row2object(self, row: pd.Series) -> User:
        return User(str(row.name), row)


class Entity(NamedObject):
    pass

class Entities(NamedObjects[Entity]):
    name: str = "entities"
    
    def row2object(self, row: pd.Series) -> Entity:
        return Entity(str(row.name), row)


class Social(Row):
    pass

class Socials(FilteredTable[Social]):
    TableRowType: type = Social
    name: str = "socials"
    default_keynames: list[str] = ["by", "to", "kind"]
    default_default_values: dict[str, Any] = dict(weight=0., timestamp=0)
    default_default_select: Select = SelectLast("timestamp")


class PublicSetting(Row):
    pass

class PublicSettings(FilteredTable[PublicSetting]):
    TableRowType: type = PublicSetting
    name: str = "public_settings"
    default_column_names: list[str] = ["username", "entity_name"]
    default_keynames: list[str] = ["username", "entity_name"]
    default_default_values: dict[str, Any] = dict(public=True)
    default_dtypes: dict[str, DTypeLike] = dict(public=np.bool_)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def default_public_value(self) -> bool:
        return self.default_values["public"]

    def penalties(self, privacy_penalty: float) -> NDArray[np.float64]:
        return self("public", self.default_public_value) * privacy_penalty

    def penalty(self, privacy_penalty: float, *args, **kwargs) -> float:
        if self.get(*args, **kwargs).get("public", self.default_public_value):
            return 1
        return privacy_penalty
    

class Rating(Row):
    default_default_values: dict[str, Any] = dict(criterion="main", context="undefined")

class Ratings(FilteredTable[Rating]):
    TableRowType: type = Rating
    name: str = "ratings"
    default_column_names = ["username", "entity_name", "criterion", "context", "timestamp"]
    default_keynames: list[str] = ["username", "entity_name", "criterion", "context"]
    default_default_select: Select = SelectLast("timestamp")


class Comparison(Row):
    default_default_values: dict[str, Any] = dict(criterion="main", context="undefined")

class Comparisons(FilteredTable[Comparison]):
    TableRowType: type = Comparison
    name: str = "comparisons"
    default_column_names: list[str] = [
        "username", "criterion", "context", "left_name", "right_name", "timestamp"]
    default_keynames = ["username", "criterion", "context", "left_name", "right_name"]
    default_default_select: Select = SelectLast("timestamp")

    def entity_comparisons(self, 
        entities: Entities,
        default_value: float = 1.,
        default_max: float = np.inf,
    ) -> list[tuple[NDArray[np.int64], NDArray[np.float64], NDArray[np.float64]]]:
        """ Returns other_indices, comparison_values, comparison_maxs """
        return [
            self._single_entity_comparisons(entity, entities, default_value, default_max)
            for entity in entities
        ]

    def _single_entity_comparisons(self, 
        entity: Entity,
        entities: Entities,
        default_value: float = 1.,
        default_max: float = np.inf,
    ) -> tuple[NDArray[np.int64], NDArray[np.float64], NDArray[np.float64]]:
        """ Returns other_indices, comparison_values, comparison_maxs """
        as_left = self.filters(left_name=entity.name)
        lother_indices = [entities.name2index(r) for r in as_left("right_name")]
        lvalues = as_left("value", default_value)
        lmaxs = as_left("max", default_max)
        as_right = self.filters(right_name=entity.name)
        rother_indices = [entities.name2index(l) for l in as_right("left_name")]
        rvalues = - as_right("value", default_value)
        rmaxs = as_right("max", default_max)
        other_indices = np.array(lother_indices + rother_indices, dtype=np.int64)
        values = np.concatenate([lvalues, rvalues], dtype=np.float64)
        maxs = np.concatenate([lmaxs, rmaxs], dtype=np.float64)
        return other_indices, values, maxs


class VotingRight(Row):
    default_value: dict[str, Any] = dict(voting_right=1.)

class VotingRights(FilteredTable[VotingRight]):
    TableRowType: type = VotingRight
    name: str = "voting_rights"
    default_column_names: list[str] = ["username", "entity_name", "criterion", "voting_right"]
    default_keynames: list[str] = ["username", "entity_name", "criterion"]
    default_default_values: dict[str, Any] = dict(voting_right=0.)
    default_dtypes: dict[str, DTypeLike] = dict(voting_right=np.float64)

    def get(self, select: Select | None = None, **keys: Hashable) -> VotingRight:
        """ For convenience, if VotingRight is the same for all entities,
        then it may have be set without entity_name as a keyname. """
        if "entity_name" in keys and "entity_name" not in self.keynames:
            del keys["entity_name"]
        return super().get(select, **keys)


class PastRecommendation(Row):
    default: dict[str, Any] = dict()

class PastRecommendations(FilteredTable[PastRecommendation]):
    TableRowType: type = PastRecommendation
    name: str = "past_recommendations"
    default_column_names: list[str] = ["username", "entity_name", "context", "timestamp"]
    default_keynames: list[str] = ["username", "entity_name", "context"]
    