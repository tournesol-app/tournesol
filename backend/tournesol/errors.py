from rest_framework import status
from rest_framework.exceptions import APIException


class ConflictError(APIException):
    """
    Usually occurs when the data of an HTTP PUT is inconsistent with the database's state
    """
    status_code = status.HTTP_409_CONFLICT
