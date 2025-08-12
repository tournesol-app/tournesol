from django.db.models.signals import post_save
from django.dispatch import receiver

from tournesol.models import Comparison, ContributorRating


# pylint: disable=unused-argument
@receiver(post_save, sender=Comparison)
def initialize_ratings_on_comparison_creation(sender, instance, created, **kwargs):
    comparison: Comparison = instance

    if not created:
        comparison.mark_compared_entities_as_seen()
        return

    ContributorRating.objects.update_or_create(
        poll_id=comparison.poll_id,
        user_id=comparison.user_id,
        entity_id=comparison.entity_1_id,
        defaults={"entity_seen": True},
    )

    ContributorRating.objects.update_or_create(
        poll_id=comparison.poll_id,
        user_id=comparison.user_id,
        entity_id=comparison.entity_2_id,
        defaults={"entity_seen": True},
    )
