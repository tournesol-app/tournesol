from zoneinfo import ZoneInfo

from django.db import models
from django.utils.html import format_html


class TalkEntry(models.Model):
    name = models.SlugField(
        unique=True,
        help_text="Unique reference of the talk",
    )
    date = models.DateTimeField(
        help_text="Date and time when the talk (please mind the server time zone).",
        null=True,
        default=None,
        blank=True,
    )
    invitation_link = models.URLField(
        help_text="the invitation link of the talk",
        null=True,
        blank=True,
    )
    youtube_link = models.URLField(
        help_text="the youtube link of the talk",
        null=True,
        blank=True,
    )
    speakers = models.TextField(
        help_text="Speakers of the talk and short description",
        null=True,
        blank=True,
    )
    title = models.CharField(
        help_text="the title of the talk",
        null=True,
        blank=True,
        max_length=255,
    )
    abstract = models.TextField(
        help_text="Description of the content of the talk",
        null=True,
        blank=True,
    )
    display = models.BooleanField(
        help_text='Determine if talk is display on frontend',
        default=False
    )

    class Meta:
        ordering = ["date"]
        verbose_name = "Talk Entry"
        verbose_name_plural = "Talk Entries"

    def __str__(self) -> str:
        return self.name

    def get_date_gmt(self):
        """Return the date in time zone Europe/Paris."""
        if self.date:
            return self.date.astimezone(ZoneInfo('Europe/Paris')).strftime('%Y-%m-%dT%H:%M:%S%z')
        return None

    def html_youtube_link(self):
        if not self.youtube_link:
            return None

        return format_html('<a href="{}" target="_blank">Play ▶</a>', self.youtube_link)
