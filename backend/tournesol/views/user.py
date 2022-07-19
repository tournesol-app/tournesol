import logging

from django.contrib.auth import logout
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


class CurrentUserView(APIView):
    """Manage the deletion of the authenticated user."""
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={204: None})
    def delete(self, request):
        """
        Delete and logout the authenticated user.
        All related resources are also deleted: comparisons, rate-later list, access tokens, etc.
        """
        user = request.user
        user.delete()
        logout(request)
        logger.info(
            "User '%s' with email '%s' has been deleted.", user.username, user.email
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
