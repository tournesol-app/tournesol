from typing import Optional
from zoneinfo import ZoneInfo

from django.db import models
from django.utils.html import format_html
from django.utils.text import slugify


class TalkEntry(models.Model):
    EVENT_TYPE_LIVE = "live"
    EVENT_TYPE_TALK = "talk"

    EVENT_TYPE = {
        (EVENT_TYPE_LIVE, "Tournesol Live"),
        (EVENT_TYPE_TALK, "Tournesol Talk"),
    }

    title = models.CharField(
        help_text="The title of the event.",
        unique=True,
        max_length=255,
    )
    name = models.SlugField(
        help_text="Used as an URL slug. Leave it blank to automatically build it from the title.",
        blank=True,
        unique=True,
        max_length=255,
    )
    event_type = models.CharField(max_length=16, choices=EVENT_TYPE, default=EVENT_TYPE_TALK)
    date = models.DateTimeField(
        help_text="Date and time of the event according to the server time.",
        null=True,
        blank=True,
    )
    invitation_link = models.URLField(
        help_text="Allows the users to join the event.",
        null=True,
        blank=True,
    )
    youtube_link = models.URLField(
        help_text="The YouTube link of the recorded event.",
        null=True,
        blank=True,
    )
    speakers = models.TextField(
        help_text="A list of speakers and their titles (researcher, PhD student, etc.).",
        null=True,
        blank=True,
    )
    abstract = models.TextField(
        help_text="Description of the event.",
        null=True,
        blank=True,
    )
    public = models.BooleanField(
        help_text="If False, the event should not be returned by the API.", default=False
    )

    class Meta:
        ordering = ["-date"]
        verbose_name = "Tournesol Event"

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = slugify(self.title)

        super().save(*args, **kwargs)

    def date_as_tz_europe_paris(self) -> Optional[str]:
        if self.date:
            return self.date.astimezone(ZoneInfo("Europe/Paris")).strftime("%Y-%m-%dT%H:%M:%S%z")
        return None

    def html_youtube_link(self):
        if not self.youtube_link:
            return None

        return format_html('<a href="{}" target="_blank">Play ▶</a>', self.youtube_link)
