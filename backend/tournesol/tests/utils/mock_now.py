from contextlib import contextmanager
from datetime import datetime, timezone
from unittest.mock import patch


class MockNow:
    """
    Test utils class to mock the current date.

    Can be used as decorator or context manager.

    Example:
    
        @MockNow.Context()
        def my_test():
            ...

        with MockNow.Context(datetime(1337, 1, 1)) as mock_now:
            ...

    """

    DEFAULT_DATE = datetime(2020, 1, 1, tzinfo=timezone.utc)

    @contextmanager
    def Context(now = DEFAULT_DATE):
        with patch("django.utils.timezone.now", lambda: now) as mock_now:
            yield mock_now
