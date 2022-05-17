from tournesol.models import Poll
from tournesol.suggestions.suggester import Suggester


class _SuggesterStore:
    suggesters: dict[Poll, Suggester] = {}

    def get_suggester(self, poll: Poll) -> Suggester:
        if poll not in self.suggesters.keys():
            self.suggesters[poll] = Suggester(poll)
        return self.suggesters[poll]


class SuggesterStore:
    actual_store = _SuggesterStore()
