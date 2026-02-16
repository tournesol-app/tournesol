from solidago.poll import *
from solidago.poll_functions.poll_function import PollFunction


class SimpleStats(PollFunction):
    def __call__(self, 
        users: Users,
        entities: Entities,
        ratings: Ratings,
        comparisons: Comparisons,
    ) -> tuple[Users, Entities]:
        return SimpleStats.users(users, ratings, comparisons), SimpleStats.entities(entities, ratings, comparisons)

    @staticmethod
    def users(users: Users, ratings: Ratings, comparisons: Comparisons) -> Users:
        return users.assign(
            n_ratings=[len(ratings.filters(username=user.name)) for user in users], 
            n_comparisons=[len(comparisons.filters(username=user.name)) for user in users], 
            n_evaluated_entities=[
                len(
                    ratings.filters(username=user.name).keys("entity_name") | \
                        comparisons.filters(username=user.name).keys("left_name") | \
                        comparisons.filters(username=user.name).keys("right_name")
                ) for user in users
            ]
        )
    
    @staticmethod
    def entities(entities: Entities, ratings: Ratings, comparisons: Comparisons) -> Entities:
        return entities.assign(
            n_ratings=[len(ratings.filters(entity_name=entity.name)) for entity in entities], 
            n_comparisons=[
                len(comparisons.filters(left_name=entity.name)) + len(comparisons.filters(right_name=entity.name)) 
                for entity in entities
            ], 
            n_raters=[len(ratings.filters(entity_name=entity.name).keys("username")) for entity in entities], 
            n_comparers=[
                len(comparisons.filters(entity_name=entity.name).keys("username")) \
                    + len(comparisons.filters(entity_name=entity.name).keys("username")) 
                for entity in entities
            ], 
            n_evaluators=[
                len(
                    ratings.filters(entity_name=entity.name).keys("username") | \
                        comparisons.filters(entity_name=entity.name).keys("username") | \
                        comparisons.filters(entity_name=entity.name).keys("username")
                ) for entity in entities
            ]
        )
