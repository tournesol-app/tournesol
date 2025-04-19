from typing import Optional
from django.db.models import F, Q

import pandas as pd
import solidago

from tournesol.models import VotingRights


class VotingRights(solidago.VotingRights):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def load(cls, poll_name: str, *args, **kwargs) -> "VotingRights":
        """ In the current Tournesol implementation, voting rights are not saved.
        This must be fixed to facilitate online updates. """
        return VotingRights()
        # values = VotingRights.objects.filter(
            # voting_rights__poll__name=directory,
        # ).values(
            # username=F("user_id"), 
            # entity_name=F("entity_id"), 
            # criterion=F("criterion"),
            # value=F("value"),
        # )
        # init_data = pd.DataFrame(values) if len(values) > 0 else None
        # return cls(init_data=init_data, *args, **kwargs)

    def save(self, poll_name: str, name: str="vouches", **kwargs) -> tuple[str, dict]:
        """ In the current Tournesol implementation, voting rights are not saved. """
        return self.save_instructions(directory, name)
