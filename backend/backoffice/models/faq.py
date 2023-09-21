# pylint: disable=duplicate-code

from django.conf import settings
from django.db import models

from core.models.mixin import LocalizedFieldsMixin


class FAQEntry(LocalizedFieldsMixin, models.Model):
    """
    An entry of a FAQ (Frequently Asked Questions).

    A `FAQEntry` consists of a question and an answer, both translated in zero
    or more languages.

    Entries cannot be grouped by tag for now, but could be in the future.
    """

    name = models.SlugField(unique=True, help_text="The unique identifier of the question.")
    rank = models.IntegerField(help_text="Allows to order the questions.")
    enabled = models.BooleanField(
        default=True, help_text="Disabled questions shouldn't be displayed by the API."
    )

    class Meta:
        ordering = ["rank"]
        verbose_name = "FAQ Entry"
        verbose_name_plural = "FAQ Entries"

    def __str__(self) -> str:
        return self.name

    def get_question_text_prefetch(self, lang=None):
        """Return the translated text of the question."""
        return self.get_localized_text_prefetch(
            related="questions", field="text", lang=lang, default=self.name
        )

    def get_answer_text_prefetch(self, lang=None):
        """Return the translated text of the answer."""
        return self.get_localized_text_prefetch(
            related="answers", field="text", lang=lang, default=self.name
        )


class FAQuestionLocale(models.Model):
    """
    A translated question of a `FAQEntry`.
    """

    question = models.ForeignKey(FAQEntry, on_delete=models.CASCADE, related_name="questions")
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

    question = models.ForeignKey(FAQEntry, on_delete=models.CASCADE, related_name="answers")
    language = models.CharField(max_length=10, choices=settings.LANGUAGES)
    text = models.TextField()

    class Meta:
        unique_together = ["question", "language"]
        verbose_name = "FAQ Answer Locale"

    def __str__(self) -> str:
        return self.text
