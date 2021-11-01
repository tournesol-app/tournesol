import logging
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import User, EmailDomain

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=User)
def ensure_that_email_domain_exists(sender, instance, update_fields, **kwargs):
    if update_fields is not None and 'email' not in update_fields:
        # Email is unchanged. No need to create the EmailDomain.
        return

    user: User = instance
    if not user.email:
        return
    if '@' not in user.email:
        # Should never happen, as the address format is already validated at this point.
        logger.warning(
            'Cannot find email domain for user "%s" with email "%s".',
            user.username, user.email
        )
        return
    _, domain_part = user.email.rsplit('@', 1)
    domain = f"@{domain_part}".lower()
    EmailDomain.objects.get_or_create(domain=domain)
