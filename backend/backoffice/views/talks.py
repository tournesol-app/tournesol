from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.generics import ListAPIView

from backoffice.models import TalkEntry
from backoffice.serializers import TalkEntrySerializer


@extend_schema_view(
    get=extend_schema(
        description="List all scheduled public Talks.",
    ),
)
class TalkEntryListView(ListAPIView):
    permission_classes = []
    queryset = TalkEntry.objects.none()
    serializer_class = TalkEntrySerializer

    def get_queryset(self):
        qst = TalkEntry.objects.all().filter(public=True, date__isnull=False).order_by("-date")
        return qst
