from abc import ABC, abstractmethod

from tournesol.models import Poll


class ContributionSuggestionStrategy(ABC):
    """
    Abstract Base Class for all contribution suggestion strategies.
    """

    def __init__(self, request, poll: Poll):
        self.request = request
        self.poll = poll

    @abstractmethod
    def get_result(self):
        raise NotImplementedError
