from rest_framework.views import exception_handler
from rest_framework.response import Response
from django.db.utils import IntegrityError
from .helpers import GenericErrorSerializer


def handler(exc, context):
    """Custom exception handler."""
    # Call REST framework's default exception handler first,
    # to get the standard error response.

    s = GenericErrorSerializer

    if type(exc) == OverflowError:
        response = Response(s(s.PK_ERROR).data, status=400)
    elif type(exc) == IntegrityError:
        response = Response(s(s.DB_ERROR).data, status=400)
    else:
        response = exception_handler(exc, context)
    return response
