"""Utils methods related to time."""

from datetime import timedelta

from django.utils import timezone


def time_ago(**kwargs):
    """Return a time in the past as specified as keyword arguments."""

    return timezone.now() - timedelta(**kwargs)


def time_ahead(**kwargs) -> datetime:
    """
    Return a `datetime` in the future relative to now.

    The keyword arguments are directly passed to `datetime.timedelta`.
    """

    return timezone.now() + timedelta(**kwargs)
