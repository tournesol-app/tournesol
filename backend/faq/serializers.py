"""
Serializers of the `faq` app.
"""

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from faq.models import FAQuestion


class FAQuestionSerializer(ModelSerializer):
    """
    A translated question with its translated answer.
    """

    question = serializers.CharField(source="get_text")
    answer = serializers.CharField(source="answer.get_text")

    class Meta:
        model = FAQuestion
        fields = ["name", "question", "answer"]
