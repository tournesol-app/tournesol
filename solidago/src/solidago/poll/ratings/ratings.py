from typing import Any, TYPE_CHECKING, Union
from pandas import Series

from solidago.primitives.datastructure import NestedDict, MultiKeyTable

if TYPE_CHECKING:
    from solidago.poll.entities import Entity

class Rating:
    def __init__(self, 
        value: float | None = None,
        min: float | None = None,
        max: float | None = None,
        root_law: str | None = None,
        context: str = "undefined",
        **kwargs
    ):
        self.value = float("nan") if value is None else value
        self.min = -float("inf") if min is None else min
        self.max = float("inf") if max is None else max
        assert isinstance(self.value, (int, float)), self.value
        assert isinstance(self.min, (int, float)), self.min
        assert isinstance(self.max, (int, float)), self.max
        self.root_law = root_law
        self.context = context
    
    @classmethod
    def from_series(cls, row: Series) -> "Rating":
        return cls(**dict(row))

    @property
    def keynames(self) -> tuple:
        return "value", "min", "max"

    def to_tuple(self) -> tuple:
        return self.value, self.min, self.max
    
    def to_series(self) -> Series:
        return Series(dict(zip(self.keynames, self.to_tuple())))

    def __repr__(self) -> str:
        return f"{self.value} (min={self.min}, max={self.max})"


class Ratings(MultiKeyTable):
    name: str="ratings"
    value_cls: type=Rating
    default_keynames: tuple=("username", "criterion", "entity_name")

    @property
    def valuenames(self) -> tuple:
        return self.value_cls().keynames

    def value2tuple(self, rating: Rating) -> tuple:
        return rating.to_tuple()
    
    def series2value(self, previous_stored_value: Any, row: Series) -> Rating:
        return Rating.from_series(row)

    def get_evaluators(self, entity: Union[str, "Entity"]) -> set[str]:
        return { username for username in self.get(entity_name=entity).keys("username") }

    def has_default_type(self) -> bool:
        return type(self) == Rating and self.keynames == self.default_keynames
