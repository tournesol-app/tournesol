from django.db.models import Count
from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.generics import ListAPIView

from backoffice.models import Banner, FAQEntry, TalkEntry
from backoffice.serializers import BannerSerializer, FAQEntrySerializer, TalkEntrySerializer


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
        description="List all active banners.",
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
            .prefetch_related("locales")
            .order_by("date_start", "date_end", "-priority")
        )

        return qst


@extend_schema_view(
    get=extend_schema(
        description="List all questions and their answers, translated in a specific language.",
    ),
)
class FAQEntryLocalizedListView(ListAPIView):
    """
    List all questions and their answers, translated in a specific language.

    To list all questions / answers in all available languages, use a
    different view.

    See `FAQEntry.get_localized_text()`.
    """

    permission_classes = []
    queryset = FAQEntry.objects.none()
    serializer_class = FAQEntrySerializer

    def get_queryset(self):
        # Questions without answer are excluded.
        queryset = (
            FAQEntry.objects.filter(enabled=True)
            .annotate(_n_answers=Count("answers"))
            .filter(_n_answers__gt=0)
            .prefetch_related("questions", "answers")
            .order_by("rank")
        )
        return queryset
