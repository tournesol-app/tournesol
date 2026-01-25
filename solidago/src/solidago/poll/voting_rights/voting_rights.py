from typing import Any
from pandas import Series
import numbers

from solidago.primitives.datastructure import NestedDict, MultiKeyTable


class VotingRights(MultiKeyTable):
    name: str="voting_rights"
    value_cls: type=numbers.Number
    default_keynames: tuple=("username", "entity_name", "criterion")
    
    @classmethod
    def value_factory(cls):
        return 0
        
    @property
    def valuenames(self) -> tuple[str, str]:
        return ("voting_right",)

    def series2value(self, previous_value: Any, row: Series) -> float:
        return row["voting_right"]

    def has_default_type(self) -> bool:
        return type(self) == VotingRights and self.keynames == self.default_keynames
