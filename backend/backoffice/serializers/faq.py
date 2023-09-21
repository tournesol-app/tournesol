from rest_framework import serializers

from backoffice.models import FAQEntry


class FAQEntrySerializer(serializers.ModelSerializer):
    """
    A translated question with its translated answer.
    """

    question = serializers.CharField(source="get_question_text_prefetch")
    answer = serializers.CharField(source="get_answer_text_prefetch")

    class Meta:
        model = FAQEntry
        fields = ["name", "question", "answer"]
