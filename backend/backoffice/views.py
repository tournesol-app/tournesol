"""
API of the `backoffice` app.
"""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.generics import ListAPIView

from backoffice.models import TalkEntry
from backoffice.serializers import TalkEntrySerializer


@extend_schema_view(
    get=extend_schema(
        description="List all talks incoming or past, translated in a specific language.",
    ),
)
class TalkEntryListView(ListAPIView):
    """
    List all talks incoming or past
    """

    permission_classes = []
    queryset = TalkEntry.objects.none()
    serializer_class = TalkEntrySerializer

    def get_queryset(self):
        queryset = (
            TalkEntry.objects.all().filter(display=True)
        )
        return queryset
