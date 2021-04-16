"""Middleware to get the current username.

From https://stackoverflow.com/questions/10991460/django-get-current-user-in-model-save
"""

from threading import current_thread
from django.utils.deprecation import MiddlewareMixin


# cached requests
_requests = {}


def current_request():
    """Return request being processed."""
    return _requests.get(current_thread().ident, None)


def current_user():
    """Returns user in the current request."""
    return current_request().user


class RequestMiddleware(MiddlewareMixin):
    """Save current request."""

    def process_request(self, request):
        _requests[current_thread().ident] = request

    def process_response(self, request, response):
        # when response is ready, request should be flushed
        _requests.pop(current_thread().ident, None)
        return response

    def process_exception(self, request, exception):
        # if an exception has happened, request should be flushed too
        _requests.pop(current_thread().ident, None)
