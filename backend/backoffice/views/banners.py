from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.generics import ListAPIView

from backoffice.models import Banner
from backoffice.serializers import BannerSerializer


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
