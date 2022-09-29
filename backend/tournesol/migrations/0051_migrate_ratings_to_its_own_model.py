# Generated by Django 4.0.7 on 2022-09-29 08:31

from django.db import migrations


def migrate_forward(apps, schema_editor):
    entity_model = apps.get_model("tournesol", "Entity")
    poll_model = apps.get_model("tournesol", "Poll")

    poll_videos = poll_model.objects.get(name="videos")
    poll_presidentielle2022 = poll_model.objects.get(name="presidentielle2022")

    for entity in entity_model.objects.filter(type="video").iterator():
        create_entity_poll_rating(apps, poll_videos, entity)

    for entity in entity_model.objects.filter(type="candidate_fr_2022").iterator():
        create_entity_poll_rating(apps, poll_presidentielle2022, entity)


def create_entity_poll_rating(apps, poll, entity):
    entity_pr_model = apps.get_model("tournesol", "EntityPollRating")
    # `get_or_create` allows to run the migration back and forth
    entity_pr_model.objects.get_or_create(
        poll=poll,
        entity=entity,
        tournesol_score=entity.tournesol_score,
        n_comparisons=entity.rating_n_ratings,
        n_contributors=entity.rating_n_contributors,
    )


class Migration(migrations.Migration):
    dependencies = [
        ("tournesol", "0050_add_entitypollrating_unique_together"),
    ]

    operations = [migrations.RunPython(migrate_forward, migrations.RunPython.noop)]
