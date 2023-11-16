from django.conf import settings
from django.db import models

from core.models.mixin import LocalizedFieldsMixin
from tournesol.models import Poll


class EntityContext(LocalizedFieldsMixin, models.Model):
    ASSOCIATION = "ASSOCIATION"
    CONTRIBUTOR = "CONTRIBUTORS"
    ORIGIN_CHOICES = [
        (ASSOCIATION, "Association"),
        (CONTRIBUTOR, "Contributors"),
    ]

    name = models.CharField(
        unique=True,
        max_length=64,
        help_text="Human readable name, used to identify the context in the admin interface.",
    )
    origin = models.CharField(
        max_length=16,
        choices=ORIGIN_CHOICES,
        default=ASSOCIATION,
        help_text="The persons who want to share this context with the rest of the community.",
    )
    predicate = models.JSONField(
        blank=True,
        default=dict,
        help_text="A JSON object. The keys/values should match the metadata "
        "keys/values of the targeted entities.",
    )
    unsafe = models.BooleanField(
        default=False,
        help_text="If True, this context will make the targeted entities unsafe.",
    )
    enabled = models.BooleanField(
        default=False,
        help_text="If False, this context will have no effect, and won't be returned by the API.",
    )
    poll = models.ForeignKey(
        Poll,
        on_delete=models.CASCADE,
        related_name="all_entity_contexts",
        default=Poll.default_poll_pk,
    )
    created_at = models.DateTimeField(
        blank=True,
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name

    def get_context_text_prefetch(self, lang=None) -> str:
        """Return the translated text of the context."""
        return self.get_localized_text_prefetch(related="entity_context", field="text", lang=lang)


class EntityContextLocale(models.Model):
    """
    A translated text of an `EntityContext`.
    """

    context = models.ForeignKey(EntityContext, on_delete=models.CASCADE, related_name="texts")
    language = models.CharField(max_length=10, choices=settings.LANGUAGES)
    text = models.TextField()
    source_url = models.URLField()
    source_label = models.CharField(max_length=254)

    class Meta:
        unique_together = ["context", "language"]

    def __str__(self) -> str:
        return self.text
