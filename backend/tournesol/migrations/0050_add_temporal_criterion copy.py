from django.db import migrations


def migrate_forward(apps, schema_editor):
    """
    Create the new criterion `topical news` for the poll videos.
    """
    Criteria = apps.get_model("tournesol", "Criteria")
    CriteriaLocale = apps.get_model("tournesol", "CriteriaLocale")
    CriteriaRank = apps.get_model("tournesol", "CriteriaRank")
    Poll = apps.get_model("tournesol", "Poll")

    default_poll = Poll.objects.get(name="videos")

    criteria = Criteria.objects.create(name="topical_subject")
    CriteriaLocale.objects.create(criteria=criteria, language="en", label="Topical news")
    CriteriaLocale.objects.create(
        criteria=criteria, language="fr", label="Information & actualité"
    )
    CriteriaRank.objects.create(
        criteria=criteria,
        poll=default_poll,
        rank=8,
        optional=True,
    )


class Migration(migrations.Migration):

    dependencies = [
        ("tournesol", "0049_contributorratingcriteriascore_voting_right"),
    ]

    operations = [migrations.RunPython(migrate_forward, migrations.RunPython.noop)]
