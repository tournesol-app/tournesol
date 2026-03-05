from solidago.poll import *
from solidago.poll_functions.poll_function import PollFunction


class SimpleEntityStats(PollFunction):
    def fn(self, entities: Entities, ratings: Ratings, comparisons: Comparisons) -> Entities:
        return entities.assign(
            n_ratings=self.n_ratings(entities, ratings), 
            n_raters=self.n_raters(entities, ratings), 
            n_comparisons=self.n_comparisons(entities, comparisons), 
            n_comparers=self.n_comparers(entities, comparisons), 
            n_evaluators=self.n_evaluators(entities, ratings, comparisons)
        )

    def n_ratings(self, entities: Entities, ratings: Ratings) -> list[int]:
        return [len(ratings.filters(entity_name=entity.name)) for entity in entities]
    
    def n_raters(self, entities: Entities, ratings: Ratings) -> list[int]:
        return [len(ratings.filters(entity_name=entity.name).keys("username")) for entity in entities]

    def n_comparisons(self, entities: Entities, comparisons: Comparisons) -> list[int]:
        return [
            len(comparisons.filters(left_name=entity.name)) + len(comparisons.filters(right_name=entity.name)) 
            for entity in entities
        ]
    
    def n_comparers(self, entities: Entities, comparisons: Comparisons) -> list[int]:
        return [
            len(comparisons.filters(left_name=entity.name).keys("username")) \
                + len(comparisons.filters(right_name=entity.name).keys("username")) 
            for entity in entities
        ]
    
    def n_evaluators(self, entities: Entities, ratings: Ratings, comparisons: Comparisons) -> list[int]:
        return [
            len(
                ratings.filters(entity_name=entity.name).keys("username") | \
                    comparisons.filters(left_name=entity.name).keys("username") | \
                    comparisons.filters(right_name=entity.name).keys("username")
            ) for entity in entities
        ]