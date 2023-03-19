import logging

from django.contrib.auth import logout
from django.utils import timezone
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
        Deactivate and logout the authenticated user. All related resources (comparisons, etc.)
        will be deleted separately by 'delete_inactive_users' after a delay, in order to avoid
        conflicts with ml-train currently running.
        """
        user = request.user
        user.is_active = False
        user.last_login = timezone.now()

        # The email is replaced with a placeholder address, in order to allow the email
        # to be reused immediatly. Deleting the email would not work as the db expects the
        # email to be present and unique.
        deleted_user_email = user.email
        user.email = f"__deleted__{user.id}@deleted.invalid"
        user.save(update_fields=["is_active", "last_login", "email"])

        logout(request)
        logger.info(
            "User '%s' with email '%s' has been deleted.", user.username, deleted_user_email
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
