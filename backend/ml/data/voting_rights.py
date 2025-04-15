from typing import Optional
from django.db.models import F, Q

import pandas as pd
import solidago

from tournesol.models import VotingRights


class VotingRights(solidago.VotingRights):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def load(cls, directory: str, *args, **kwargs) -> "VotingRights":
        values = VotingRights.objects.filter(
            voting_rights__poll__name=directory,
        ).values(
            username=F("user_id"), 
            entity_name=F("entity_id"), 
            criterion=F("criterion"),
            value=F("value"),
        )
        init_data = pd.DataFrame(values) if len(values) > 0 else None
        return cls(init_data=init_data, *args, **kwargs)

    def save(self, directory: str, name: str="vouches", **kwargs) -> tuple[str, dict]:
        # Solidago must not modify vouches
        raise NotImplemented
