"""
API endpoints to interact with the contributor's proofs.

A proof is a signed message issued by a poll for users that meet specific
requirements.
"""

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied

from ..serializers.proof_of_vote import ProofOfVoteSerializer
from .mixins.poll import PollScopedViewMixin


@extend_schema_view(
    get=extend_schema(
        parameters=[
            OpenApiParameter(
                "keyword",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="A keyword identifying a proof. Used as an input"
                " by the signing algorithm.",
            ),
        ],
    ),
)
class ProofView(PollScopedViewMixin, generics.RetrieveAPIView):
    """
    Return a cryptographic signature of the user id, associated to the
    selected poll and optionally to the specified keyword.

    This signature can act as a proof for the users to guarantee they have an
    activated account, and optionally that they meet specific requirements
    that can be poll dependant.

    The query parameter `keyword` identifies the requested proof, and its set
    of requirements that are expected to be met by the logged-in user. Each
    set of requirements includes at least having an activated user account.

    List of accepted keywords and matching conditions:

        "" (empty): Same as "activated".

        "activated": Only check if the user has an activated account.

        "proof_of_vote": Additionally check if the user has participated in
                         the selected poll.
    """

    serializer_class = ProofOfVoteSerializer

    def get_object(self):
        poll = self.poll_from_url
        user_id = self.request.user.id

        # Only one keyword at a time is supported for now.
        keyword = self.request.query_params.get("keyword", "activated")

        if not poll.user_meets_proof_requirements(user_id, keyword):
            raise PermissionDenied

        return {
            "signature": poll.get_user_proof(user_id, keyword),
            "poll_name": poll.name,
        }
