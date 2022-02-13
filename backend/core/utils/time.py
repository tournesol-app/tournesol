"""Utils methods related to time."""

from datetime import timedelta

from django.utils import timezone


def time_ago(**kwargs):
    """Return a time in the past as specified as keyword arguments."""

    return timezone.now() - timedelta(**kwargs)
