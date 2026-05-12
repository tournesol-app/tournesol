from typing import Iterable

from solidago.poll import *
from solidago.functions.poll_function import PollFunction


class Liquid(PollFunction):
    def __init__(self, relay_name: str = "relay"):
        self.relay_name = relay_name

    def fn(self, 
        entities: Entities, 
        socials: Socials, 
        user_models: UserModels
    ) -> UserModels:
        user_directs = UserDirectScores()
        for username, model in user_models:
            direct_scores = model(entities)
            relays = socials.filters(by=username, kind=self.relay_name)
            for delegate_name, weight in zip(relays("to"), relays("weight")):
                direct_scores = direct_scores + weight * user_models[delegate_name](entities)
            user_directs = user_directs | direct_scores.add_columns(username=username)
        return UserModels(user_directs=user_directs)
    