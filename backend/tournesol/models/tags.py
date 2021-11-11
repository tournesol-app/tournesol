from django.db import models


class Tag(models.Model):
    """Tag of a video"""

    class Meta:
        verbose_name = "tag"
        verbose_name_plural = "tags"

    name = models.CharField(
        max_length=250,
        unique=True,
        help_text="Name of the tag"
    )

    def __str__(self):
        return self.name
