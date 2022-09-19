"""
Models of the `faq` app.
"""

from django.conf import settings
from django.db import models


class FAQuestion(models.Model):
    """
    A Frequently Asked Question.

    Questions cannot be grouped by tag for now, but could be in the future.
    """

    name = models.SlugField(
        unique=True, help_text="The unique identifier of the question."
    )
    rank = models.IntegerField(help_text="Allows to order the questions.")
    enabled = models.BooleanField(
        default=True, help_text="Disabled questions shouldn't be displayed by the API."
    )

    class Meta:
        ordering = ["rank"]
        verbose_name = "FAQ Question"

    def __str__(self) -> str:
        return self.name


class FAQuestionLocale(models.Model):
    """
    A translated `FAQuestion`.
    """

    question = models.ForeignKey(
        FAQuestion, on_delete=models.CASCADE, related_name="locales"
    )
    language = models.CharField(max_length=10, choices=settings.LANGUAGES)
    text = models.CharField(max_length=255)

    class Meta:
        unique_together = ["question", "language"]
        verbose_name = "FAQ Question Locale"

    def __str__(self) -> str:
        return self.text


class FAQAnswerLocale(models.Model):
    """
    A translated answer to a `FAQuestion`.
    """

    question = models.OneToOneField(
        FAQuestion, on_delete=models.CASCADE, related_name="answers"
    )
    language = models.CharField(max_length=10, choices=settings.LANGUAGES)
    text = models.TextField()

    class Meta:
        unique_together = ["question", "language"]
        verbose_name = "FAQ Answer Locale"

    def __str__(self) -> str:
        return self.text
