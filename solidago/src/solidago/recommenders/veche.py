from solidago.poll import *
from .recommender import Recommender


class Veche(Recommender):
    def __call__(self, 
        poll: Poll, 
        username: str, 
        limit: int, 
        cursor: str | None = None
    ) -> Entities:
        user = poll.users[username]
        followings = poll.socials.get(by=username, kind="follow")
        raise NotImplemented
        


        
    