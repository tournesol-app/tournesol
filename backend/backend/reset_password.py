import logging

from annoying.functions import get_object_or_None
from backend.models import ResetPasswordToken, DjangoUser, VerifiableEmail
from backend.send_email_thread import send_email_possibly_threaded
from backend.user_verify import get_token
from django_react import settings


def send_email(targets, token):
    """Send verification e-mail to a destination."""
    domain = settings.EMAIL_PAGE_DOMAIN
    domain += '/' if not domain.endswith('/') else ''

    kwargs = {'token': token, 'domain': domain}
    send_email_possibly_threaded(subject="Password reset",
                                 template="mail_body_password_reset.txt",
                                 destination=targets,
                                 from_=settings.EMAIL_PASSWORDRESET_ADDRESS,
                                 kwargs=kwargs,
                                 template_html=None)
    logging.info(
        f"Resetting password for {targets}")


def reset_token(token, delete_token=True):
    """Delete given token. Returns user or None."""
    tokens = ResetPasswordToken.objects.filter(token=token)

    if not tokens:
        return None
    else:
        user = tokens.get().user
        if delete_token:
            tokens.delete()
        return user


def reset_password(username, do_send_mail=True):
    """Reset password for a username (send e-mail with a link)."""
    print("Resetting password for", username)
    user = get_object_or_None(DjangoUser, username=username)
    if user is None:
        raise ValueError("User not found")

    # deleting any old tokens
    ResetPasswordToken.objects.filter(user=user).delete()

    # creating a new token
    token = get_token()
    ResetPasswordToken.objects.create(user=user,
                                      token=token)

    # sending the e-mail
    emails = VerifiableEmail.objects.filter(user__user=user,
                                            is_verified=True).values('email')
    emails = [x['email'] for x in emails]

    if do_send_mail:
        print("Sending email to", emails, token)
        send_email(emails, token)

    return token
