"""
API of the `faq` app.
"""

from django.db.models import Count
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.generics import ListAPIView

from faq.models import FAQuestion
from faq.serializers import FAQuestionSerializer


@extend_schema_view(
    get=extend_schema(
        description="List all questions and their answers, translated in a specific language.",
    ),
)
class FAQuestionLocalizedListView(ListAPIView):
    """
    List all questions and their answers, translated in a specific language.

    To list all questions / answers in all available languages, use a
    different view.

    See `FAQuestsion.get_text()`.
    """

    permission_classes = []
    queryset = FAQuestion.objects.none()
    serializer_class = FAQuestionSerializer

    def get_queryset(self):
        # Questions without answer are excluded.
        queryset = (
            FAQuestion.objects.filter(enabled=True)
            .annotate(_n_answers=Count("answers"))
            .filter(_n_answers__gt=0)
            .prefetch_related("locales", "answers")
            .order_by("rank")
        )
        return queryset
