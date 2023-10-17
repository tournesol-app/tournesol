from abc import ABC, abstractmethod

from tournesol.models import Poll


class ContributionSuggestionStrategy(ABC):
    """
    Abstract Base Class for all contribution suggestion strategies.

    A contribution can be an entity to compare, a comparison to make, etc.
    """

    def __init__(self, request, poll: Poll):
        self.request = request
        self.poll = poll

    @abstractmethod
    def get_result(self):
        raise NotImplementedError

    @abstractmethod
    def get_serializer_class(self):
        """
        Return a DRF serializer class that should be used to serialize the
        result returned by `get_result()`.
        """
        raise NotImplementedError
