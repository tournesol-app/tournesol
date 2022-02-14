import logging

from rest_framework.generics import RetrieveAPIView

from tournesol.models import Poll
from tournesol.serializers import PollSerializer

logger = logging.getLogger(__name__)


class PollsView(RetrieveAPIView):
    """
    Retrieve a poll and its related criteria.
    """
    permission_classes = []
    queryset = Poll.objects.prefetch_related("criteriarank_set__criteria")
    lookup_field = "name"
    serializer_class = PollSerializer
