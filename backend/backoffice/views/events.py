from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework.generics import ListAPIView

from backoffice.models import TalkEntry
from backoffice.serializers import TournesolEventSerializer


@extend_schema_view(
    get=extend_schema(
        description="List all scheduled Tournesol events.",
        parameters=[
            OpenApiParameter(
                name="event_type",
                description="Filter the events by type.",
                enum=[event_type[0] for event_type in TalkEntry.EVENT_TYPE],
                required=False,
            ),
        ],
    ),
)
class TournesolEventListView(ListAPIView):
    permission_classes = []
    queryset = TalkEntry.objects.none()
    serializer_class = TournesolEventSerializer

    def get_queryset(self):
        event_type = self.request.query_params.get("event_type")

        qst = TalkEntry.objects.filter(
            public=True,
            date__isnull=False,
        )

        if event_type:
            qst = qst.filter(event_type=event_type)

        return qst.order_by("-date")
