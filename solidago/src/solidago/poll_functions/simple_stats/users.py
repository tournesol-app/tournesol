from solidago.poll import *
from solidago.poll_functions.poll_function import PollFunction


class SimpleUserStats(PollFunction):
    def fn(self, users: Users, ratings: Ratings, comparisons: Comparisons) -> Users:
        return users.assign(
            n_ratings=self.n_ratings(users, ratings), 
            n_comparisons=self.n_comparisons(users, comparisons), 
            n_evaluated_entities=self.n_evaluated_entities(users, ratings, comparisons),
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