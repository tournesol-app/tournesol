from typing import Optional
from django.db.models import F, Q

import pandas as pd
import solidago

from tournesol.models import Voucher


class Vouches(solidago.Vouches):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def load(cls, *args, **kwargs) -> "Vouches":
        """ Vouches are common to all polls """
        values = Voucher.objects.filter(
            by__is_active=True,
            to__is_active=True,
        ).values(
            by=F("by__id"),
            to=F("to__id"),
            weight=F("value"),
        )
        if len(values) > 0:
            init_data = pd.DataFrame(values)
            init_data["priority"] = 0
        else:
            init_data = pd.DataFrame(columns=["by", "to", "weight", "priority"])
        return cls(init_data, *args, **kwargs)

    def save(self, name: str="vouches", **kwargs) -> tuple[str, dict]:
        # Solidago must not modify vouches
        raise NotImplemented
