from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils import translation

from .poll import Poll


class Criteria(models.Model):
    """
    Model that just contains the name of the criteria.

    The same criteria name can be used in multiple polls, and for multiple languages.
    """
    name = models.SlugField(unique=True)

    def __str__(self) -> str:
        return self.name

    def get_label(self, lang=None):
        if lang is None:
            lang = translation.get_language()
        try:
            locale = self.locales.get(language=lang)
        except ObjectDoesNotExist:
            try:
                locale = self.locales.get(language="en")
            except ObjectDoesNotExist:
                return self.name
        return locale.label


class CriteriaRank(models.Model):
    class Meta:
        ordering = ["poll", "-rank", "pk"]
        unique_together = ["criteria", "poll"]

    criteria = models.ForeignKey(Criteria, on_delete=models.CASCADE)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    rank = models.IntegerField(default=0)
    optional = models.BooleanField(default=True)


class CriteriaLocale(models.Model):
    """Criteria localization model"""
    class Meta:
        unique_together = ["criteria", "language"]

    criteria = models.ForeignKey(Criteria, on_delete=models.CASCADE, related_name="locales")
    language = models.CharField(max_length=10, choices=settings.LANGUAGES)
    label = models.CharField(max_length=255)
