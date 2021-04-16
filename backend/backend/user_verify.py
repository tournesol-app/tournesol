import logging
import secrets

from backend.black_white_email_domain import is_domain_accepted, is_domain_rejected, get_domain
from backend.models import VerifiableEmail
from backend.send_email_thread import send_email_possibly_threaded
from django.conf import settings


def get_token():
    """Get a random token for the e-mail."""
    return secrets.token_urlsafe(50)


def send_verification_email(email: VerifiableEmail):
    """Send verification e-mail to a destination."""
    if not email.is_verified:
        email.token = get_token()
        email.save()

        send_verification_email_thread(email=email.email, token=email.token)
        logging.info(
            f"Sending verification email for {email} with token {email.token}")


def send_verification_email_thread(email, token):
    """Send the confirmation e-mail."""
    assert email and token, ("Supply an address and a token.", email, token)
    domain = settings.EMAIL_PAGE_DOMAIN
    domain += '/' if not domain.endswith('/') else ''
    link = domain + 'email_verify?token=%s' % token

    email_domain = get_domain(email)
    kwargs = {'link': link, 'is_accepted': is_domain_accepted(email_domain),
              'is_rejected': is_domain_rejected(email_domain)}

    send_email_possibly_threaded(subject=settings.EMAIL_MAIL_SUBJECT,
                                 template=settings.EMAIL_MAIL_PLAIN,
                                 destination=[email],
                                 from_=settings.EMAIL_ADDRESS, kwargs=kwargs,
                                 template_html=settings.EMAIL_MAIL_HTML)


def verify_email(email: VerifiableEmail, token: str):
    """If token matches the desired token, verify the e-mail."""
    if email.token and email.token == token and not email.is_verified:
        logging.info(f"Verifying e-mail {email}")
        email.is_verified = True
        email.save()

        # making the user active if it was not
        django_user = email.user.user
        if not django_user.is_active:
            django_user.is_active = True
            django_user.save()
        return email.email
    else:
        raise ValueError("Invalid token")


def verify_email_by_token(token: str):
    """Verify e-mail by token."""
    try:
        email = VerifiableEmail.objects.get(token=token)
        return verify_email(email, token)
    except VerifiableEmail.DoesNotExist:
        raise ValueError("Invalid token")
