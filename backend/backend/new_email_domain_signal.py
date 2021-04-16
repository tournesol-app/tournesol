import logging

from backend.models import EmailDomain
from backend.send_email_thread import send_email_possibly_threaded
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_react import settings


def send_email(instance):
    """Send verification e-mail to a destination."""
    domain = settings.EMAIL_PAGE_DOMAIN
    domain += '/' if not domain.endswith('/') else ''

    kwargs = {'domain': domain, 'id': instance.id, 'email_domain': instance.domain}
    send_email_possibly_threaded(subject="New pending e-mail domain added",
                                 template="mail_body_emaildomain.txt",
                                 template_html=None,
                                 destination=settings.ADMIN_EMAILS,
                                 from_=settings.EMAIL_NEWDOMAIN_ADDRESS,
                                 kwargs=kwargs)
    logging.info(
        f"Informing admins about new email domain {domain}")


@receiver(post_save, sender=EmailDomain)
def send_to_le(sender, instance, created, raw, using, update_fields, **kwargs):
    """Send an e-mail to Le when a new e-mail domain is created."""
    if created and instance.status == EmailDomain.STATUS_PENDING:
        send_email(instance)
