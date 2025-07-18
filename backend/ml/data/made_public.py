from typing import Optional
from django.db.models import F, Q

import pandas as pd
import solidago

from tournesol.models import ContributorRating


class MadePublic(solidago.MadePublic):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def load(cls, poll_name: str, *args, **kwargs) -> "MadePublic":
        values = ContributorRating.objects.filter(
            poll__name=poll_name,
        ).values(
            username=F("user_id"),
            entity_name=F("entity_id"),
            public=F("is_public"),
        )
        init_data = pd.DataFrame(values) if len(values) > 0 else None
        return cls(*args, init_data=init_data, **kwargs)

    def save(self, poll_name: str, name: str="made_public", **kwargs) -> tuple[str, dict]:
        # Solidago must not modify made_public
        raise NotImplemented