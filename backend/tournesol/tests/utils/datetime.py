from datetime import datetime
from unittest.mock import patch

from django.utils import timezone


def FixDatetime(now=lambda: datetime(2019, 1, 4, tzinfo=timezone.utc)):
    def wrapper(func):
        @patch("django.utils.timezone.now", now)
        def wrapper_func(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper_func
    return wrapper
