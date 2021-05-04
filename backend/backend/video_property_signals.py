import logging

from backend.models import EmailDomain, Video, VideoRatingPrivacy, ExpertRating, UserInformation,\
    VerifiableEmail
from backend.send_email_thread import send_email_possibly_threaded
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django_react import settings
from django.db.models import Q
import logging


# Video properties can be affected by VideoRatingPrivacy, ExpertRating,
#  UserInformation, EmailDomain, VerifiableEmail

def update_video(v):
    """Recompute properties for a video."""
    # TODO: only save when something has changed
    logging.warning(f"update_video:{v}")
    for field in Video.COMPUTED_PROPERTIES:
        getattr(v, field)
    v.save()


def update_user_username(username):
    """Recompute properties for all rated videos for a user."""
    rated = Video.objects.filter(Q(expertrating_video_1__user__user__username=username) |
                                 Q(expertrating_video_2__user__user__username=username))
    for v in rated:
        update_video(v)


def update_email(verifiable_email):
    """Recompute properties for a user given an email."""
    if verifiable_email.user is not None:
        username = verifiable_email.user.user.username
        update_user_username(username)

# EmailDomain -> VerifiableEmail -> UserInformation -> ExpertRating -> Video
#                                                VideoRatingPrivacy ->

# EmailDomain
@receiver(post_save, sender=EmailDomain)
def save_emaildomain(sender, instance, created, raw, using, update_fields, **kwargs):
    emails = VerifiableEmail.objects.filter(domain=instance.domain)
    for email in emails:
        update_email(email)


@receiver(post_delete, sender=EmailDomain)
def delete_emaildomain(sender, instance, using, **kwargs):
    emails = VerifiableEmail.objects.filter(domain=instance.domain)
    for email in emails:
        update_email(email)


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
    update_video(instance.video_1)
    update_video(instance.video_2)


@receiver(post_delete, sender=ExpertRating)
def delete_expertrating(sender, instance, using, **kwargs):
    update_video(instance.video_1)
    update_video(instance.video_2)


# VideoRatingPrivacy
@receiver(post_save, sender=VideoRatingPrivacy)
def save_videoratingprivacy(sender, instance, created, raw, using, update_fields, **kwargs):
    update_video(instance.video)


@receiver(post_delete, sender=VideoRatingPrivacy)
def delete_videoratingprivacy(sender, instance, using, **kwargs):
    update_video(instance.video)