from tournesol.models import Poll
from tournesol.suggestions.suggestionprovider import SuggestionProvider


class _SuggesterStore:
    suggesters: dict[Poll, SuggestionProvider] = {}

    def get_suggester(self, poll: Poll) -> SuggestionProvider:
        if poll not in self.suggesters.keys():
            self.suggesters[poll] = SuggestionProvider(poll)
        return self.suggesters[poll]


class SuggesterStore:
    actual_store = _SuggesterStore()
