
from django.db import models


class TalkEntry(models.Model):
    name = models.SlugField(
        unique=True,
        help_text="the reference of the talk",
    )
    date = models.DateTimeField(
        help_text="Timestamp when the talk will take place or its broadcast date",
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
    speaker = models.CharField(
        help_text="the speaker of the talk",
        null=True,
        blank=True,
        max_length=50
    )
    speaker_short_desc = models.CharField(
        help_text="A short biography of speaker",
        null=True,
        blank=True,
        max_length=50
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
