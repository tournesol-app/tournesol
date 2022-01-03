import logging

from django.db import migrations, models
from django.db.models import Count, Window, F
from django.db.models.functions.window import RowNumber


def remove_duplicated_email(apps, schema_editor):
    """
    Find users with duplicated emails, and update email of the accounts associated
    with the fewer comparisons (to preserve only 1 per original address).
    Their 'email' value will be replaced with an invalid address derived
    from the username to guarantee uniqueness in the database.
    """
    User = apps.get_model("core", "User")

    duplicated_emails = (
        User.objects.values("email").alias(count=Count("id")).filter(count__gte=2)
    )
    users_to_update = [
        user
        for user in User.objects.filter(email__in=duplicated_emails).annotate(
            n_comparisons=Count("comparisons"),
            rank_comparisons=Window(
                expression=RowNumber(),
                partition_by=[F("email")],
                order_by=F("n_comparisons").desc(),
            ),
        )
        if user.rank_comparisons > 1
    ]

    for u in users_to_update:
        new_email = f"{u.username}@invalid"
        logging.info(
            'Updating email for user "%s", from "%s" to "%s"',
            u.username,
            u.email,
            new_email,
        )
        u.email = new_email
        u.save(update_fields=["email"])


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0004_rename_userpreferences_userpreference"),
        ("tournesol", "0015_remove_obsolete_fields"),
    ]

    operations = [
        migrations.RunPython(
            code=remove_duplicated_email, reverse_code=migrations.RunPython.noop
        ),
        migrations.AlterField(
            model_name="user",
            name="email",
            field=models.EmailField(
                max_length=254, unique=True, verbose_name="email address"
            ),
        ),
    ]
