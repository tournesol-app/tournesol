"""
EntitySourceLink model.

Links an entity to one of the sources that produced it. The links of an entity
are derived from its metadata, and are kept in sync each time it is saved.
"""

from django.db import models

from tournesol.models.entity_source import EntitySource


class EntitySourceLink(models.Model):
    """A link between an entity and one of the sources that produced it."""

    entity = models.ForeignKey(
        to="tournesol.Entity",
        on_delete=models.CASCADE,
        related_name="source_links",
    )
    entity_source = models.ForeignKey(
        to=EntitySource,
        on_delete=models.CASCADE,
        related_name="entity_links",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["entity", "entity_source"]

    def __str__(self):
        return f"entity:{self.entity_id}/source:{self.entity_source_id}"
