from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.generics import ListAPIView

from backoffice.models.banner import Banner
from backoffice.models.talk import TalkEntry
from backoffice.serializers import BannerSerializer, TalkEntrySerializer


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


@extend_schema_view(
    get=extend_schema(
        description="List all enabled banners.",
    ),
)
class BannerListView(ListAPIView):
    permission_classes = []
    queryset = Banner.objects.none()
    serializer_class = BannerSerializer

    def get_queryset(self):
        now = timezone.now()
        qst = (
            Banner.objects.all()
            .filter(enabled=True, date_start__lte=now, date_end__gte=now)
            .prefetch_related("texts", "titles")
            .order_by("date_start", "date_end", "-priority")
        )

        return qst
