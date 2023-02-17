from contextlib import contextmanager
from datetime import datetime
from unittest.mock import patch

from django.utils import timezone


class MockNow:

    DefaultDate = datetime(2020, 1, 1, tzinfo=timezone.utc)

    @contextmanager
    def Context(now = DefaultDate):
        with patch("django.utils.timezone.now", lambda: now) as mock_now:
            yield mock_now
