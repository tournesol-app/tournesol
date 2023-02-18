"""Utils methods related to time."""

from datetime import datetime, timedelta

from django.utils import timezone


def time_ago(**kwargs):
    """
    Return a `datetime` in the past relative to now.

    The keyword arguments are directly passed to `datetime.timedelta`.
    """

    return timezone.now() - timedelta(**kwargs)


def time_ahead(**kwargs) -> datetime:
    """
    Return a `datetime` in the future relative to now.

    The keyword arguments are directly passed to `datetime.timedelta`.
    """

    return timezone.now() + timedelta(**kwargs)
