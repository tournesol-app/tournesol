from django.db import migrations


def forward_func(apps, schema_editor):
    """
    Create missing instances of ContributorRating for all existing Comparisons
    (including non-trusted users, for which no rating has been computed by ML),
    in order to store the 'is_public' flag related to every pair (user, video).
    """
    ContributorRating = apps.get_model("tournesol", "ContributorRating")
    Comparison = apps.get_model("tournesol", "Comparison")
    user_video_pairs = set(
        Comparison.objects.all().values_list("user_id", "video_1_id").distinct()
    )
    user_video_pairs.update(
        Comparison.objects.all().values_list("user_id", "video_2_id").distinct()
    )
    ContributorRating.objects.bulk_create(
        [
            ContributorRating(user_id=user_id, video_id=video_id)
            for (user_id, video_id) in user_video_pairs
        ],
        batch_size=1000,
        ignore_conflicts=True,
    )


class Migration(migrations.Migration):
    dependencies = [
        ("tournesol", "0013_add_tag_model"),
    ]

    operations = [
        migrations.RunPython(code=forward_func, reverse_code=migrations.RunPython.noop)
    ]
