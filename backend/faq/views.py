"""
API of the `faq` app.
"""

from django.db.models import Count
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.generics import ListAPIView

from faq.models import FAQEntry
from faq.serializers import FAQEntrySerializer


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

    See `FAQEntry.get_text()`.
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
