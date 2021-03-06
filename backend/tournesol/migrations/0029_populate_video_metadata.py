# Generated by Django 4.0.2 on 2022-02-22 09:59

from django.db import migrations

from tournesol.serializers.metadata import VideoMetadata

def migrate_forward(apps, schema_editor):
    """
    For all videos, populate entity 'metadata' JSON field 
    based on values from legacy model fields.
    """
    Entity = apps.get_model("tournesol", "Entity")
    for entity in Entity.objects.filter(type="video").iterator():
        metadata_serializer = VideoMetadata(data={
            "source": "youtube",
            "video_id": entity.video_id,
            "name": entity.name or "",
            "description": entity.description or "",
            "uploader": entity.uploader or "",
            "publication_date": entity.publication_date.isoformat() if entity.publication_date else None,
            "duration": int(entity.duration.total_seconds()) if entity.duration else None,
            "views": entity.views,
            "language": entity.language,
            "tags": list(entity.tags.values_list("name", flat=True)),
            "is_unlisted": entity.is_unlisted
        })
        metadata_serializer.is_valid(raise_exception=True)
        entity.metadata = metadata_serializer.data
        entity.save(update_fields=["metadata"])


class Migration(migrations.Migration):

    dependencies = [
        ('tournesol', '0028_remove_contributorrating_poll_default'),
    ]

    operations = [migrations.RunPython(migrate_forward, migrations.RunPython.noop)]

