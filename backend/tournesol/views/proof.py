"""
API endpoints to interact with the contributor's proofs of work and other
kind of proof.
"""

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied

from tournesol.serializers.proof_of_vote import ProofOfVoteSerializer

from ..models import Comparison
from .mixins.poll import PollScopedViewMixin


@extend_schema_view(
    get=extend_schema(
        parameters=[
            OpenApiParameter(
                "keyword",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Used as an input by the signing algorithm.",
            ),
        ],
    ),
)
class ProofView(PollScopedViewMixin, generics.RetrieveAPIView):
    """
    Return a cryptographic signature of the user id, associated to the
    selected poll and optionally to the specified keyword.

    This signature can act as a proof for the users to guarantee they really
    have an account, and optionally that they meet specific expectations that
    can be poll dependant.

    The query parameter `keyword` specifies which set of conditions are
    expected to be met by the logged-in user. Each set of conditions
    includes at least having a user account.

    List of accepted keywords and matching conditions:

        "" (empty): Only check if the user has an account.

        "proof_of_vote": Additionally check if the user has participated in
                         the selected poll.
    """

    _proof_of_vote_keyword = "proof_of_vote"

    serializer_class = ProofOfVoteSerializer

    def user_has_voted(self, poll, user):
        """
        Return True if the user has at least one comparison in the given poll,
        False instead.

        TODO: This method, and potentially similar future methods should be
              implemented by the `Poll` model, not by the view, in order to
              follow the simple view / complex model pattern recommended by
              the Django community. The view doesn't need to know the
              strategies used by the model to check if the users meet the
              expectations. Calling a single Poll's method with the proper
              arguments should be enough.
        """
        comparisons = Comparison.objects.filter(poll=poll, user=user)

        if comparisons.exists():
            return True
        return False

    def get_object(self):
        user = self.request.user
        poll = self.poll_from_url
        # Only one keyword at a time is supported for now
        keyword = self.request.query_params.get("keyword", "")

        if keyword == self._proof_of_vote_keyword:
            has_voted = self.user_has_voted(poll, user)
            if not has_voted:
                raise PermissionDenied

        return {
            "signature": poll.get_user_proof(self.request.user.id, keyword),
            "poll_name": poll.name,
        }
