from django.db.models import F, Q
from pandas import DataFrame

import solidago
from tournesol.models import Entity


class Entities(solidago.Entities):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def load(cls, poll_name: str, *args, **kwargs) -> "Entities":
        # TODO: Lê does not know the database well enough
        raise NotImplemented

    def save(self, poll_name: str, name: str="entities", **kwargs) -> tuple[str, dict]:
        # TODO: Lê does not know the database well enough
        raise NotImplemented
        return self.save_instructions(name)
