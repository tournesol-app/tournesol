from abc import ABC, abstractmethod
from typing import Optional

from core.models import User
from tournesol.models import Poll


class ContributionSuggestionStrategy(ABC):
    """
    Abstract Base Class for all contribution suggestion strategies.

    A contribution can be a list of entities to compare, or comparisons to
    make, etc.
    """

    def __init__(self, poll: Poll, user: User, languages: Optional[list[str]] = None):
        self.poll = poll
        self.user = user
        self.languages = languages

    @abstractmethod
    def get_results(self):
        raise NotImplementedError
