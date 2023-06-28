from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils import translation


class Banner(models.Model):
    name = models.CharField(
        help_text="The banner's name",
        blank=False,
        unique=True,
        max_length=255,
    )
    date_start = models.DateTimeField(
        help_text="Date at which the banner should start to be displayed",
        blank=False,
    )
    date_end = models.DateTimeField(
        help_text="Date after which the banner should stop being displayed",
        blank=False,
    )
    security_advisory = models.BooleanField(
        help_text="If True, the banner should be displayed in priority",
        default=False,
    )
    enabled = models.BooleanField(
        help_text="If False, the banner should not be displayed",
        default=True,
    )

    class Meta:
        ordering = ["-date_start", "-date_end"]
        verbose_name = "Banner"
        verbose_name_plural = "Banners"

    def __str__(self) -> str:
        return self.name

    def get_text(self, related="texts", lang=None):
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

    def get_text_prefetch(self, related="texts", lang=None):
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

    def get_content_prefetch(self, lang=None):
        return self.get_text_prefetch(related="texts", lang=lang)

    def get_title_prefetch(self, lang=None):
        return self.get_text_prefetch(related="titles", lang=lang)


class BannerTitle(models.Model):
    banner = models.ForeignKey(
        Banner,
        on_delete=models.CASCADE,
        related_name="titles",
    )
    title = models.CharField(
        blank=False,
        max_length=255,
    )
    language = models.CharField(
        blank=False,
        max_length=10,
        choices=settings.LANGUAGES,
    )

    class Meta:
        unique_together = ["banner", "language"]
        verbose_name = "Banner Title"
        verbose_name_plural = "Banner Titles"

    def __str__(self) -> str:
        return self.title


class BannerText(models.Model):
    banner = models.ForeignKey(
        Banner,
        on_delete=models.CASCADE,
        related_name="texts",
    )
    text = models.TextField(
        blank=False,
    )
    language = models.CharField(
        blank=False,
        max_length=10,
        choices=settings.LANGUAGES,
    )

    class Meta:
        unique_together = ["banner", "language"]
        verbose_name = "Banner Text"
        verbose_name_plural = "Banner Texts"

    def __str__(self) -> str:
        return self.text


class BannerActionLabel(models.Model):
    banner = models.ForeignKey(
        Banner,
        on_delete=models.CASCADE,
        related_name="action_labels",
    )
    action_label = models.CharField(
        blank=False,
        max_length=255,
    )
    language = models.CharField(
        blank=False,
        max_length=10,
        choices=settings.LANGUAGES,
    )

    class Meta:
        unique_together = ["banner", "language"]
        verbose_name = "Banner Action Label"
        verbose_name_plural = "Banner Action Labels"

    def __str__(self) -> str:
        return self.action_label


class BannerActionLink(models.Model):
    banner = models.ForeignKey(
        Banner,
        on_delete=models.CASCADE,
        related_name="links",
    )
    url = models.URLField(
        blank=False,
    )
    language = models.CharField(
        blank=False,
        max_length=10,
        choices=settings.LANGUAGES,
    )

    class Meta:
        unique_together = ["banner", "language"]
        verbose_name = "Banner Link"
        verbose_name_plural = "Banner Links"

    def __str__(self) -> str:
        return self.url
