from typing import Optional

import pandas as pd
import solidago

from tournesol.models import ComparisonCriteriaScore


class Comparison(solidago.Comparison):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        
class Comparisons(solidago.Comparisons):
    name: str="comparisons"
    value_factory: Callable=Comparison
    value_cls: type=Comparison
    
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
        init_data = self.query_init_data(criterion, username)
        super().__init__(keynames, init_data, parent_tuple, *args, **kwargs)

    def query_init_data(self, criterion=None, user_id=None) -> pd.DataFrame:
        scores_queryset = ComparisonCriteriaScore.objects.filter(
            comparison__poll__name=self.poll_name,
            comparison__user__is_active=True,
        )
        if criterion is not None:
            scores_queryset = scores_queryset.filter(criteria=criterion)

        if user_id is not None:
            scores_queryset = scores_queryset.filter(comparison__user_id=user_id)

        values = scores_queryset.values(
            "score",
            "score_max",
            "weight",
            criterion=F("criteria"),
            entity_a=F("comparison__entity_1_id"),
            entity_b=F("comparison__entity_2_id"),
            user_id=F("comparison__user_id"),
        )
        if len(values) > 0:
            dtf = pd.DataFrame(values)
            return dtf[
                ["user_id", "entity_a", "entity_b", "criterion", "score", "score_max", "weight"]
            ].rename({ 
                "public_username": "username",
                "video_a": "left_name",
                "video_b": "right_name",
                "criteria": "criterion",
                "score": "value",
                "score_max": "max"
            })

        return pd.DataFrame(
            columns=[
                "username",
                "left_name",
                "right_name",
                "criterion",
                "value",
                "max",
                "weight",
            ]
        )
