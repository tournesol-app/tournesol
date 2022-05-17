import pytest

from tournesol.models import Poll
from tournesol.suggestions.graph import Graph
from tournesol.suggestions.suggester_store import SuggesterStore


@pytest.mark.unit
def test_class_instantiation():
    local_poll = Poll.default_poll()
    graph = Graph(None, local_poll, local_poll.criterias[0])
    suggester = SuggesterStore.actual_store.get_suggester(local_poll)
