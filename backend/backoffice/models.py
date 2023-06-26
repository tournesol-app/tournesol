import datetime
from typing import Optional
from zoneinfo import ZoneInfo

from django.db import models
from django.utils.html import format_html


class TalkEntry(models.Model):
    title = models.CharField(
        help_text="The title of the Talk.",
        max_length=255,
    )
    name = models.SlugField(
        unique=True,
        help_text="Unique identifier of the Talk (usable as an URL slug).",
    )
    date = models.DateTimeField(
        help_text="Date and time of the Talk (please mind the server time zone).",
        null=True,
        blank=True,
    )
    invitation_link = models.URLField(
        help_text="Allow the users to join the Talk.",
        null=True,
        blank=True,
    )
    youtube_link = models.URLField(
        help_text="The Talk's YouTube link.",
        null=True,
        blank=True,
    )
    speakers = models.TextField(
        help_text="A list of speakers and their titles (researcher, PhD student, etc.).",
        null=True,
        blank=True,
    )
    abstract = models.TextField(
        help_text="Description of the Talk.",
        null=True,
        blank=True,
    )
    display = models.BooleanField(
        help_text="If False, the Talk should not be returned by the API.",
        default=False
    )

    class Meta:
        ordering = ["-date"]
        verbose_name = "Talk Entry"
        verbose_name_plural = "Talk Entries"

    def __str__(self) -> str:
        return self.name

    def date_as_tz_europe_paris(self) -> Optional[datetime.datetime]:
        if self.date:
            return self.date.astimezone(ZoneInfo('Europe/Paris'))
        return None

    def html_youtube_link(self):
        if not self.youtube_link:
            return None

        return format_html('<a href="{}" target="_blank">Play ▶</a>', self.youtube_link)
