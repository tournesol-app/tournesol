import numpy as np

from solidago.poll import *
from solidago.functions.poll_function import PollFunction
from solidago.primitives.datastructure.named_objects import Contains
from .filtering import Filtering


class RemoveAuthoredEntities(PollFunction):
    def __init__(self, username: str | None = None):
        super().__init__(max_workers=1)
        self.username = username
    
    def fn(self, poll: Poll) -> Poll:
        assert self.username is not None, f"{type(self).__name__} without user"
        publications = poll.entities.filters(authors=Contains(self.username))
        entity_names = set(poll.entities.names()) - set(publications.names())
        return Filtering(entity_names=entity_names)(poll)
