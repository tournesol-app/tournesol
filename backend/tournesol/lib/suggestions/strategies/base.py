from abc import ABC, abstractmethod

from core.models import User
from tournesol.models import Poll


class ContributionSuggestionStrategy(ABC):
    """
    Abstract Base Class for all contribution suggestion strategies.

    A contribution can be a list of entities to compare, or comparisons to
    make, etc.
    """

    def __init__(self, poll: Poll, user: User):
        self.poll = poll
        self.user = user

    @abstractmethod
    def get_results(self):
        raise NotImplementedError

    @abstractmethod
    def get_serializer_class(self):
        """
        Return a DRF serializer class that should be used to serialize the
        results returned by `get_results()`.
        """
        raise NotImplementedError
