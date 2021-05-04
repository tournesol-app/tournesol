import logging

from backend.models import EmailDomain, Video, VideoRatingPrivacy, ExpertRating, UserInformation,\
    VerifiableEmail
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Q
from time import time


# maximal number of updates done within the same thread
MAX_IN_LIST = 5


# Video properties can be affected by VideoRatingPrivacy, ExpertRating,
#  UserInformation, EmailDomain, VerifiableEmail


def clamp_list(lst, max_len=MAX_IN_LIST):
    """If the list is too long, print a warning and reduce the length."""
    # TODO: immediately start a background job?
    if len(lst) > max_len:
        logging.warning("List is too long to perform updates. "
                        "The updates will be done later via the cron job.")
        return None
    return lst


# do not update recently updated videos
RECENTLY_UPDATED_TIMESTAMP = {}
RECENTLY_UPDATED_DELTA_S = 10


def update_video(v, delta_s=RECENTLY_UPDATED_DELTA_S):
    """Recompute properties for a video."""

    time_now = time()
    if v.id in RECENTLY_UPDATED_TIMESTAMP and time_now - RECENTLY_UPDATED_TIMESTAMP[v.id] < delta_s:
        return

    # TODO: only save when something has changed
    logging.warning(f"update_video:{v}")
    for field in Video.COMPUTED_PROPERTIES:
        getattr(v, field)
    v.save()

    RECENTLY_UPDATED_TIMESTAMP[v.id] = time_now


def update_user_username(username, force_fast=False):
    """Recompute properties for all rated videos for a user."""
    rated = Video.objects.filter(Q(expertrating_video_1__user__user__username=username) |
                                 Q(expertrating_video_2__user__user__username=username))

    rated_to_update = clamp_list(rated)
    if rated_to_update is None or force_fast:
        rated.update(is_update_pending=True)
    else:
        for v in rated_to_update:
            update_video(v)


def update_email(verifiable_email, force_fast=False):
    """Recompute properties for a user given an email."""

    # user might be deleted!
    try:
        user = verifiable_email.user
    except UserInformation.DoesNotExist:
        return

    if user is not None:
        username = user.user.username
        update_user_username(username, force_fast=force_fast)

# EmailDomain -> VerifiableEmail -> UserInformation -> ExpertRating -> Video
#                                                VideoRatingPrivacy ->


# EmailDomain
@receiver(post_save, sender=EmailDomain)
def save_emaildomain(sender, instance, created, raw, using, update_fields, **kwargs):
    emails = VerifiableEmail.objects.filter(domain=instance.domain)

    lst = clamp_list(emails)
    for email in emails:
        update_email(email, force_fast=lst is None)


@receiver(post_delete, sender=EmailDomain)
def delete_emaildomain(sender, instance, using, **kwargs):
    emails = VerifiableEmail.objects.filter(domain=instance.domain)

    lst = clamp_list(emails)
    for email in emails:
        update_email(email, force_fast=lst is None)


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
    # done instantly
    update_video(instance.video_1)
    update_video(instance.video_2)


@receiver(post_delete, sender=ExpertRating)
def delete_expertrating(sender, instance, using, **kwargs):
    # done instantly
    update_video(instance.video_1)
    update_video(instance.video_2)


# VideoRatingPrivacy
@receiver(post_save, sender=VideoRatingPrivacy)
def save_videoratingprivacy(sender, instance, created, raw, using, update_fields, **kwargs):
    # done instantly
    update_video(instance.video)


@receiver(post_delete, sender=VideoRatingPrivacy)
def delete_videoratingprivacy(sender, instance, using, **kwargs):
    # done instantly
    update_video(instance.video)
