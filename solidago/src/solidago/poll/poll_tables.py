from typing import Any, Literal
from numpy.typing import DTypeLike, NDArray

import numpy as np, pandas as pd

from solidago.primitives.datastructure import Row, FilteredTable
from solidago.primitives.datastructure.named_objects import NamedObject, NamedObjects


class User(NamedObject):
    default: dict[str, bool | int | float | str] = dict(pretrust=False, trust=0.0)

class Users(NamedObjects[User]):
    name: str = "users"
    
    def row2object(self, row: pd.Series) -> User:
        return User(str(row.name), row)


class Entity(NamedObject):
    default: dict[str, bool | int | float | str] = dict()

class Entities(NamedObjects[Entity]):
    name: str = "entities"
    
    def row2object(self, row: pd.Series) -> Entity:
        return Entity(str(row.name), row)


class Social(Row):
    default: dict[str, Any] = dict(weight=0.0, priority=-0.0)

class Socials(FilteredTable[Social]):
    TableRowType: type = Social
    name: str = "socials"
    default_column_names: list[str] = ["by", "to", "kind", "weight", "priority"]
    default_keynames: set[str] = {"by", "to", "kind"}
    default_dtypes: dict[str, DTypeLike] = dict(weight=np.float64, priority=np.float64)


class PublicSetting(Row):
    default: dict[str, Any] = dict(public=True)

class PublicSettings(FilteredTable[PublicSetting]):
    TableRowType: type = PublicSetting
    name: str = "public_settings"
    default_column_names: list[str] = ["username", "entity_name", "public"]
    default_keynames: set[str] = {"username", "entity_name"}
    default_dtypes: dict[str, DTypeLike] = dict(public=np.bool_)

    def penalties(self, privacy_penalty: float) -> NDArray[np.float64]:
        return self.get_column("public", np.float64) * privacy_penalty # type: ignore

    def penalty(self, privacy_penalty: float, *args, **kwargs) -> float:
        public_setting = self.get(*args, **kwargs)
        assert isinstance(public_setting, PublicSetting)
        return 1 if public_setting["public"] else privacy_penalty
    

class Rating(Row):
    default: dict[str, Any] = dict(
        value=np.nan, min=-np.inf, max=np.inf,
        root_law=None, root_law_arg=None, 
        context="undefined",
    )

class Ratings(FilteredTable[Rating]):
    TableRowType: type = Rating
    name: str = "ratings"
    default_column_names: list[str] = ["username", "entity_name", "criterion", "context", 
        "value", "min", "max", "root_law", "root_law_arg"]
    default_keynames: set[str] = {"username", "entity_name", "criterion", "context"}
    default_dtypes: dict[str, DTypeLike] = dict(value=np.float64, min=np.float64, max=np.float64)
    default_select: Literal['unique', 'first', 'last'] = "last"


class Comparison(Row):
    default: dict[str, Any] = dict(
        value=np.nan, max=np.inf,
        root_law=None, root_law_arg=None, 
        context="undefined",
    )

class Comparisons(FilteredTable[Comparison]):
    TableRowType: type = Comparison
    name: str = "comparisons"
    default_column_names: list[str] = ["username", "criterion", "context", "left_name", "right_name",
        "value", "max", "root_law", "root_law_arg"]
    default_keynames: set[str] = {"username", "criterion", "context", "left_name", "right_name"}
    default_dtypes: dict[str, DTypeLike] = dict(value=np.float64, max=np.float64)
    default_select: Literal['unique', 'first', 'last'] = "last"

    def entity_comparisons(self, entities: Entities) -> list[tuple[NDArray[np.int64], NDArray[np.float64], NDArray[np.float64]]]:
        """ Returns other_indices, comparison_values, comparison_maxs """
        result = list()
        for entity in entities:
            as_left = self.filters(left_name=entity.name)
            as_left_other_indices = [entities.name2index(right_name) for right_name in as_left.get_column("right_name")]
            as_left_values = as_left.get_column("value").to_numpy(np.float64)
            as_left_maxs = as_left.get_column("max").to_numpy(np.float64)
            as_right = self.filters(right_name=entity.name)
            as_right_other_indices = [entities.name2index(left_name) for left_name in as_right.get_column("left_name")]
            as_right_values = - as_right.get_column("value").to_numpy(np.float64)
            as_right_maxs = as_right.get_column("max").to_numpy(np.float64)
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


class PastRecommendation(Row):
    pass

class PastRecommendations(FilteredTable[PastRecommendation]):
    TableRowType: type = PastRecommendation
    name: str = "past_recommendations"
    default_column_names: list[str] = ["username", "entity_name", "context", "timestamp"]
    default_keynames: set[str] = {"username", "entity_name", "context"}
    default_dtypes: dict[str, DTypeLike] = dict(timestamp=np.int64)
