"""
API endpoints to show public statistics
"""

from rest_framework import generics
from rest_framework.exceptions import PermissionDenied

from tournesol.serializers.proof_of_vote import ProofOfVoteSerializer

from ..models import Comparison
from .mixins.poll import PollScopedViewMixin


class ProofOfVoteView(PollScopedViewMixin, generics.RetrieveAPIView):
    """
    API for retrievring proof_of_vote in a given poll
    """
    serializer_class = ProofOfVoteSerializer

    def get_object(self):
        poll = self.poll_from_url
        comparisons = Comparison.objects.filter(
            user=self.request.user,
            poll=poll,
        )

        if not comparisons.exists():
            raise PermissionDenied

        return {
            "signature": poll.get_proof_of_vote(self.request.user.id),
            "poll_name": poll.name,
        }
