from django.db import migrations

def migrate_forward(apps, schema_editor):
    """
    Convert number of views from str to int in metadata
    """
    Entity = apps.get_model("tournesol", "Entity")
    for entity in Entity.objects.filter(type="video").iterator():
        views = entity.metadata.get("views")
        if isinstance(views, str):
            entity.metadata["views"] = int(views)
            entity.save(update_fields=["metadata"])


class Migration(migrations.Migration):

    dependencies = [
        ('tournesol', '0038_alter_entitycriteriascore_unique_together_and_more'),
    ]

    operations = [migrations.RunPython(migrate_forward, migrations.RunPython.noop)]

