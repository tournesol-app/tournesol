from typing import Optional

import pandas as pd
import solidago

from tournesol.models import ContributorRating


class MadePublic(solidago.MadePublic):
    def __init__(self, 
        keynames: list=[],
        init_data: None,
        parent_tuple: Optional[tuple["Comparisons", tuple, tuple]]=None,
        username: Optional[str]=None, 
        criterion: Optional[str]=None, 
        *args, **kwargs
    ):
        keynames = list()
        if username is not None:
            keynames.append("username")
        if criterion is not None:
            keynames.append("criterion")
        keynames += ["entity_name", "other_name"]
        if init_data is None:
            init_data = self.query_init_data(criterion, username)
        super().__init__(keynames, init_data, parent_tuple, *args, **kwargs)

    def init_data(self):
        # This makes sure that `get_scaling_calibration_users()` is evaluated separately, as the
        # table names mentionned in its RawSQL query could conflict with the current queryset.
        values = ContributorRating.objects.filter(
            poll__name=self.poll_name,
        ).values(
            "user_id",
            "entity_id",
            "is_public",
        )
        if len(values) == 0:
            return pd.DataFrame(
                columns=[
                    "user_id",
                    "entity_id",
                    "is_public",
                ]
            )
        return pd.DataFrame(values)
