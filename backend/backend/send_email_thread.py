from django_react.settings import EMAIL_USE_SINGLE_THREAD
from django.template.loader import render_to_string
from threading import Thread
from django.core.mail import send_mail
import logging


def send_email_now(subject, template, destination, from_, kwargs, template_html):
    """Send an e-mail in the current thread."""
    text = render_to_string(template, kwargs)
    html = None
    if template_html is not None:
        html = render_to_string(template_html, kwargs)
    send_mail(
        subject,
        text,
        from_,
        destination,
        fail_silently=False,
        html_message=html,
    )


def send_email_possibly_threaded(subject, template, destination, from_,
                                 template_html=None, kwargs=None):
    """Send an e-mail, possible in another thread, depending on config."""

    if kwargs is None:
        kwargs = {}

    if isinstance(destination, str):
        destination = [destination]

    assert isinstance(subject, str), subject
    assert isinstance(template, str), template
    assert isinstance(destination, list), destination
    assert isinstance(from_, str), from_
    assert isinstance(kwargs, dict), kwargs
    assert isinstance(template_html, str) or (template_html is None), template_html

    logging.info(f"Sending an e-mail from {from_} to {destination}, Subject: {subject}"
                 f" templates {template} {template_html}")

    kwargs_send = dict(subject=subject, template=template, destination=destination,
                       from_=from_, kwargs=kwargs, template_html=template_html)

    if EMAIL_USE_SINGLE_THREAD:
        logging.info("Using single thread")
        try:
            send_email_now(**kwargs_send)
        except Exception as e:
            logging.warning(f"E-mail sending failed: {str(e)}")
    else:
        logging.info("Launching a separate thread")
        Thread(target=send_email_now, kwargs=kwargs_send).start()
