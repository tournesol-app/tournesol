"""
Models of the `faq` app.
"""

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils import translation


class AbstractLocalizable(models.Model):
    """
    This class factorizes common behaviours between questions and answers.
    """

    class Meta:
        abstract = True

    def get_text(self, lang=None):
        """Return the translated text of the instance."""
        if lang is None:
            lang = translation.get_language()
        try:
            locale = self.locales.get(language=lang)
        except ObjectDoesNotExist:
            try:
                locale = self.locales.get(language="en")
            except ObjectDoesNotExist:
                return self.name  # pylint: disable=no-member
        return locale.text


class FAQuestion(AbstractLocalizable):
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


class FAQAnswer(AbstractLocalizable):
    """
    An answer to a `FAQuestion`.
    """

    name = models.SlugField(
        unique=True, help_text="The unique identifier of the answer."
    )
    question = models.OneToOneField(
        FAQuestion, on_delete=models.CASCADE, related_name="answer"
    )

    class Meta:
        verbose_name = "FAQ Answer"

    def __str__(self) -> str:
        return self.name


class FAQAnswerLocale(models.Model):
    answer = models.ForeignKey(
        FAQAnswer, on_delete=models.CASCADE, related_name="locales"
    )
    language = models.CharField(max_length=10, choices=settings.LANGUAGES)
    text = models.TextField()

    class Meta:
        unique_together = ["answer", "language"]
        verbose_name = "FAQ Answer Locale"
