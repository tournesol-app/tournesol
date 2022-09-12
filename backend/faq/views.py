"""
API of the `faq` app.
"""

from rest_framework.generics import ListAPIView

from faq.models import FAQuestion
from faq.serializers import FAQuestionSerializer


class FAQuestionLocalizedListView(ListAPIView):
    """
    List all questions and their answers, translated in a specific language.

    To list all questions / answers in all available languages, use a
    different view.

    See `FAQAnswer.get_text()` and `FAQuestsion.get_text()`.
    """

    permission_classes = []
    queryset = FAQuestion.objects.none()
    serializer_class = FAQuestionSerializer

    def get_queryset(self):
        queryset = (
            FAQuestion.objects.filter(enabled=True)
            .prefetch_related("locales")
            .order_by("rank")
        )
        return queryset
