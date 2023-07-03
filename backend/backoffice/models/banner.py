from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils import translation


class Banner(models.Model):
    name = models.CharField(
        help_text="The banner's name.",
        unique=True,
        max_length=255,
    )
    date_start = models.DateTimeField(
        help_text="Date on which the banner should be returned by the API.",
    )
    date_end = models.DateTimeField(
        help_text="After this date the banner should not be returned by the API.",
    )
    security_advisory = models.BooleanField(
        default=False,
        help_text="If True the banner is a security announcement.",
    )
    enabled = models.BooleanField(
        default=True,
        help_text="Disabled banner should not be returned by the API.",
    )
    priority = models.IntegerField(
        help_text="Allows to order the banners.",
        default=5,
    )

    class Meta:
        ordering = ["-date_start", "-date_end", "-priority"]

    def __str__(self) -> str:
        return self.name

    def get_localized_text(self, field, related="locales", lang=None):
        if lang is None:
            lang = translation.get_language()
        try:
            locale = getattr(self, related).get(language=lang)
        except ObjectDoesNotExist:
            try:
                locale = getattr(self, related).get(language="en")
            except ObjectDoesNotExist:
                return ""
        return getattr(locale, field)

    def get_localized_text_prefetch(self, field, related="locales", lang=None):
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
                return ""
        return getattr(locale, field)

    def get_title_prefetch(self, lang=None):
        return self.get_localized_text_prefetch(related="locales", lang=lang, field="title")

    def get_paragraph_prefetch(self, lang=None):
        return self.get_localized_text_prefetch(related="locales", lang=lang, field="text")

    def get_action_label_prefetch(self, lang=None):
        return self.get_localized_text_prefetch(related="locales", lang=lang, field="action_label")

    def get_url_prefetch(self, lang=None):
        return self.get_localized_text_prefetch(related="locales", lang=lang, field="url")


class BannerLocale(models.Model):
    banner = models.ForeignKey(
        Banner,
        on_delete=models.CASCADE,
        related_name="locales",
    )
    title = models.CharField(
        max_length=255,
    )
    text = models.TextField()
    action_label = models.CharField(
        max_length=255,
    )
    url = models.URLField()
    language = models.CharField(
        max_length=10,
        choices=settings.LANGUAGES,
    )

    class Meta:
        unique_together = ["banner", "language"]

    def __str__(self) -> str:
        return self.title
