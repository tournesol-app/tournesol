import logging

from backend.models import EmailDomain
from backend.send_email_thread import send_email_possibly_threaded
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_react import settings


# Video properties can be affected by VideoRatingPrivacy, ExpertRating,
#  UserInformation, EmailDomain, VerifiableEmail

@receiver(post_save, sender=EmailDomain)
def send_to_le(sender, instance, created, raw, using, update_fields, **kwargs):
    """Send an e-mail to Le when a new e-mail domain is created."""
    if created and instance.status == EmailDomain.STATUS_PENDING:
        send_email(instance)
