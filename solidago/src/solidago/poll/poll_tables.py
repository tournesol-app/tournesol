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
    default_column_names: list[str] = ["by", "to", "kind", "weight", "timestamp"]
    default_keynames: set[str] = {"by", "to", "kind"}
    default_default_select: Select = SelectLast("timestamp")


class PublicSetting(Row):
    default: dict[str, Any] = dict(public=True)

class PublicSettings(FilteredTable[PublicSetting]):
    TableRowType: type = PublicSetting
    name: str = "public_settings"
    default_column_names: list[str] = ["username", "entity_name", "public"]
    default_keynames: set[str] = {"username", "entity_name"}
    default_dtypes: dict[str, DTypeLike] = dict(public=np.bool_)
    
    def __init__(self, *args, default_value: bool = True, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_value = default_value

    def penalties(self, privacy_penalty: float) -> NDArray[np.float64]:
        return self("public", self.default_value) * privacy_penalty

    def penalty(self, privacy_penalty: float, *args, **kwargs) -> float:
        if self.get(*args, **kwargs).get("public", self.default_value):
            return 1
        return privacy_penalty
    

class Rating(Row):
    pass

class Ratings(FilteredTable[Rating]):
    TableRowType: type = Rating
    name: str = "ratings"
    default_column_names = ["username", "entity_name", "criterion", "context", "timestamp"]
    default_keynames: set[str] = {"username", "entity_name", "criterion", "context"}
    default_default_select: Select = SelectLast("date")


class Comparison(Row):
    pass

class Comparisons(FilteredTable[Comparison]):
    TableRowType: type = Comparison
    name: str = "comparisons"
    default_column_names: list[str] = ["username", "criterion", "context", 
        "left_name", "right_name", "timestamp"]
    default_keynames: set[str] = {"username", "criterion", "context", "left_name", "right_name"}
    default_default_select: Select = SelectLast("timestamp")

    def entity_comparisons(self, 
        entities: Entities,
        default_value: float = 1.,
        default_max: float = np.inf,
    ) -> list[tuple[NDArray[np.int64], NDArray[np.float64], NDArray[np.float64]]]:
        """ Returns other_indices, comparison_values, comparison_maxs """
        result = list()
        for entity in entities:
            as_left = self.filters(left_name=entity.name)
            as_left_other_indices = [entities.name2index(r) for r in as_left("right_name")]
            as_left_values = as_left("value", default_value)
            as_left_maxs = as_left("max", default_max)
            as_right = self.filters(right_name=entity.name)
            as_right_other_indices = [entities.name2index(l) for l in as_right("left_name")]
            as_right_values = - as_right("value", default_value)
            as_right_maxs = as_right("max", default_max)
            other_indices = np.array(as_left_other_indices + as_right_other_indices, dtype=np.int64)
            comparison_values = np.concatenate([as_left_values, as_right_values], dtype=np.float64)
            comparison_maxs = np.concatenate([as_left_maxs, as_right_maxs], dtype=np.float64)
            result.append((other_indices, comparison_values, comparison_maxs))
        return result


class VotingRight(Row):
    default: dict[str, Any] = dict(voting_right=0.)

class VotingRights(FilteredTable[VotingRight]):
    TableRowType: type = VotingRight
    name: str = "voting_rights"
    default_column_names: list[str] = ["username", "entity_name", "criterion", "voting_right"]
    default_keynames: set[str] = {"username", "entity_name", "criterion"}
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
    default_keynames: set[str] = {"username", "entity_name", "context"}
    