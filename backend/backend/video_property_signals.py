from backend.models import EmailDomain, Video, VideoRatingPrivacy, ExpertRating, UserInformation,\
    VerifiableEmail
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Q


# on update, mark Video as needing a property recomputation.
#  then, a cron job will make the actual update

# Video properties can be affected by VideoRatingPrivacy, ExpertRating,
#  UserInformation, EmailDomain, VerifiableEmail


def update_user_username(username):
    """Recompute properties for all rated videos for a user."""
    rated = Video.objects.filter(Q(expertrating_video_1__user__user__username=username) |
                                 Q(expertrating_video_2__user__user__username=username))

    rated.update(is_update_pending=True)


def update_videos_by_pk(pks):
    """Update all videos by their primary keys."""
    Video.objects.filter(pk__in=pks).update(is_update_pending=True)


def update_email(verifiable_email, force_fast=False):
    """Recompute properties for a user given an email."""

    # user might be deleted!
    try:
        user = verifiable_email.user
    except UserInformation.DoesNotExist:
        return

    if user is not None:
        username = user.user.username
        update_user_username(username)


def update_emaildomain(domain):
    """Recompute properties for all users with this domain."""
    rated = Video.objects.filter(
            Q(expertrating_video_1__user__user__userinformation__emails__domain=domain) |
            Q(expertrating_video_2__user__user__userinformation__emails__domain=domain))
    rated.update(is_update_pending=True)


# EmailDomain -> VerifiableEmail -> UserInformation -> ExpertRating -> Video
#                                                VideoRatingPrivacy ->


# EmailDomain
@receiver(post_save, sender=EmailDomain)
def save_emaildomain(sender, instance, created, raw, using, update_fields, **kwargs):
    update_emaildomain(instance.domain)


@receiver(post_delete, sender=EmailDomain)
def delete_emaildomain(sender, instance, using, **kwargs):
    update_emaildomain(instance.domain)


# VerifiableEmail
@receiver(post_save, sender=VerifiableEmail)
def save_email(sender, instance, created, raw, using, update_fields, **kwargs):
    update_email(instance)


@receiver(post_delete, sender=VerifiableEmail)
def delete_email(sender, instance, using, **kwargs):
    update_email(instance)


# UserInformation
@receiver(post_save, sender=UserInformation)
def save_userinformation(sender, instance, created, raw, using, update_fields, **kwargs):
    update_user_username(instance.user.username)


@receiver(post_delete, sender=UserInformation)
def delete_userinformation(sender, instance, using, **kwargs):
    update_user_username(instance.user.username)


# ExpertRating
@receiver(post_save, sender=ExpertRating)
def save_expertrating(sender, instance, created, raw, using, update_fields, **kwargs):
    update_videos_by_pk([instance.video_1.pk, instance.video_2.pk])


@receiver(post_delete, sender=ExpertRating)
def delete_expertrating(sender, instance, using, **kwargs):
    update_videos_by_pk([instance.video_1.pk, instance.video_2.pk])


# VideoRatingPrivacy
@receiver(post_save, sender=VideoRatingPrivacy)
def save_videoratingprivacy(sender, instance, created, raw, using, update_fields, **kwargs):
    update_videos_by_pk([instance.video.pk])


@receiver(post_delete, sender=VideoRatingPrivacy)
def delete_videoratingprivacy(sender, instance, using, **kwargs):
    update_videos_by_pk([instance.video.pk])
