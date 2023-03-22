"""
API endpoints to interact with the logged-in user's settings.
"""


from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.serializers.user_settings import TournesolUserSettingsSerializer


class UserSettingsDetail(generics.GenericAPIView):
    """
    This API allows to interact with all settings of the logged-in user.

    The settings of several polls can be modified in one request. As a
    consequence the path parameter `poll` is not required.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = TournesolUserSettingsSerializer

    def get(self, request):
        """
        Get the logged-in user's settings.
        """
        settings = request.user.settings
        serializer = TournesolUserSettingsSerializer(settings)
        return Response(serializer.data)

    def patch(self, request):
        """
        Update a subset of the logged-in user's settings.
        """
        user = request.user
        settings = user.settings
        serializer = TournesolUserSettingsSerializer(settings, data=request.data)

        if serializer.is_valid():
            user.settings.update(serializer.save())
            user.save(update_fields=["settings"])
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        """
        Replace the logged-in user's settings by new ones.
        """
        user = request.user
        serializer = TournesolUserSettingsSerializer(data=request.data)

        if serializer.is_valid():
            user.settings = serializer.save()
            user.save(update_fields=["settings"])
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
