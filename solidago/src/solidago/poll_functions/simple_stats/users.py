from functools import reduce

from solidago.poll import *
from solidago.poll_functions.poll_function import PollFunction
from solidago.primitives.criteria import to_criteria


class SimpleUserStats(PollFunction):
    def __init__(self, criteria: set[str] | str | None = None, max_workers: int | None = None):
        super().__init__(max_workers)
        self.criteria = {criteria} if isinstance(criteria, str) else criteria

    def fn(self, users: Users, ratings: Ratings, comparisons: Comparisons) -> Users:
        if self.criteria is None:
            criteria = {str(c) for c in comparisons.keys("criterion") | ratings.keys("criterion")}
        else:
            criteria = self.criteria
        activities_per_criterion = self.criteria_activities(users, ratings, comparisons, criteria)
        return users.assign(
            n_ratings=self.n_ratings(users, ratings), 
            n_comparisons=self.n_comparisons(users, comparisons), 
            n_evaluated_entities=self.n_evaluated_entities(users, ratings, comparisons),
            **activities_per_criterion
        )
    
    def n_ratings(self, users: Users, ratings: Ratings) -> list[int]:
        return [len(ratings.filters(username=user.name)) for user in users]
    
    def n_comparisons(self, users: Users, comparisons: Comparisons) -> list[int]:
        return [len(comparisons.filters(username=user.name)) for user in users]
    
    def n_evaluated_entities(self, users: Users, ratings: Ratings, comparisons: Comparisons) -> list[int]:
        return [
            len(
                ratings.filters(username=user.name).keys("entity_name") | \
                    comparisons.filters(username=user.name).keys("left_name") | \
                    comparisons.filters(username=user.name).keys("right_name")
            ) for user in users
        ]
    
    def criteria_activities(self, 
        users: Users, 
        ratings: Ratings, 
        comparisons: Comparisons, 
        criteria: set[str],
    ) -> dict[str, list[int]]:
        return reduce(
            lambda acc, c: acc | self.criterion_activities(users, ratings, comparisons, c), 
            criteria, 
            dict()
        ) 
        
    def criterion_activities(self,
        users: Users, 
        ratings: Ratings, 
        comparisons: Comparisons, 
        criterion: str,
    ) -> dict[str, list[int]]:
        f_ratings = ratings.filters(criterion=criterion)
        f_comparisons = comparisons.filters(criterion=criterion)
        return {
            f"n_{criterion}_ratings": self.n_ratings(users, f_ratings),
            f"n_{criterion}_comparisons": self.n_comparisons(users, f_comparisons),
            f"n_{criterion}_evaluated_entities": self.n_evaluated_entities(users, f_ratings, f_comparisons),
        }