from typing import Optional
from django.db.models import F, Q

import pandas as pd
import solidago

from tournesol.models import ComparisonCriteriaScore


class Comparisons(solidago.Comparisons):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def load(cls, directory: str, criterion=None, user_id=None, *args, **kwargs) -> "Comparisons":
        scores_queryset = ComparisonCriteriaScore.objects.filter(
            comparison__poll__name=directory,
            comparison__user__is_active=True,
        )
        if criterion is not None:
            scores_queryset = scores_queryset.filter(criteria=criterion)

        if user_id is not None:
            scores_queryset = scores_queryset.filter(comparison__user_id=user_id)

        values = scores_queryset.values(
            "weight",
            value=F("score"),
            max=F("score_max"),
            criterion=F("criteria"),
            left_name=F("comparison__entity_1_id"),
            right_name=F("comparison__entity_2_id"),
            username=F("comparison__user_id"),
        )
        init_data = pd.DataFrame(values) if len(values) > 0 else None
        return cls(*args, init_data=values, **kwargs)
    
    def save(self, directory: str, name: str="comparisons", **kwargs) -> tuple[str, dict]:
        # Solidago must not modify comparisons
        raise NotImplemented