"""
Models of the `faq` app.
"""

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils import translation


class FAQEntry(models.Model):
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

    def get_text(self, related="questions", lang=None):
        """
        Return the translated text of a related instance.

        A related instance can be a question or an answer.
        """
        if lang is None:
            lang = translation.get_language()
        try:
            locale = getattr(self, related).get(language=lang)
        except ObjectDoesNotExist:
            try:
                locale = getattr(self, related).get(language="en")
            except ObjectDoesNotExist:
                return self.name  # pylint: disable=no-member
        return locale.text

    def get_text_prefetch(self, related="questions", lang=None):
        """
        Return the translated text of a related instance.

        Contrary to `self.get_text` this method consider the related instances
        as already prefetched with `prefetch_related`, and use `.all()` instead
        of `.get()` to avoid triggering any additional SQL query.
        """
        if lang is None:
            lang = translation.get_language()

        try:
            locale = [loc for loc in getattr(self, related).all()
                      if loc.language == lang][0]

        except IndexError:
            try:
                locale = [loc for loc in getattr(self, related).all()
                          if loc.language == "en"][0]

            except IndexError:
                return self.name  # pylint: disable=no-member
        return locale.text

    def get_question_text_prefetch(self, lang=None):
        """Return the translated text of the question."""
        return self.get_text_prefetch(related="questions", lang=lang)

    def get_answer_text_prefetch(self, lang=None):
        """Return the translated text of the answer."""
        return self.get_text_prefetch(related="answers", lang=lang)


class FAQuestionLocale(models.Model):
    """
    A translated question of a `FAQEntry`.
    """

    question = models.ForeignKey(
        FAQEntry, on_delete=models.CASCADE, related_name="questions"
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
    A translated answer of a `FAQEntry`.
    """

    question = models.ForeignKey(
        FAQEntry, on_delete=models.CASCADE, related_name="answers"
    )
    language = models.CharField(max_length=10, choices=settings.LANGUAGES)
    text = models.TextField()

    class Meta:
        unique_together = ["question", "language"]
        verbose_name = "FAQ Answer Locale"

    def __str__(self) -> str:
        return self.text
