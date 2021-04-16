from enum import Enum

from rest_framework import serializers
from rest_framework.response import Response


def error_response(serializer, key='UNKNOWN', code=400):
    """Return an HTTP response with the error."""
    return Response(serializer(key).data, status=code)


def error_serializer(name=None, errors=None):
    """Create an error serializer."""

    assert name is not None, name

    # some common reasons
    default_errors = {
        'UNKNOWN': "Unknown error",
        'DB_ERROR': "Unknown database error",
        'PK_ERROR': "Invalid primary key",
        'NO_VIDEOS': "No videos in the system",
        'ALREADY_EXISTS': "Object already exists"
    }

    if errors is None:
        errors = {}
    elif isinstance(errors, dict):
        pass
    elif issubclass(errors, Enum):
        errors = {item.name: item.value for item in errors}
    else:
        raise NotImplementedError("Unknown error list, support dicts and enums")

    errors = {**default_errors, **errors}

    name = ''.join(name.split()).capitalize()
    name_cls = name + "ErrorSerializer"

    for key in errors.keys():
        assert ' ' not in key, f"Wrong key {key}"

    errors_lst = [(key, val) for key, val in errors.items()]
    help = '<br />'.join([f"<b><u>{key}</u>:</b> <i>{val}</i>" for key, val in errors.items()])

    class _ErrorSerializer(serializers.Serializer):
        f"""Serialize errors for {name}"""

        def __init__(self, *args, **kwargs):
            # allowing single-argument data
            args = list(args)
            if args and isinstance(args[0], str):
                key = args[0]
                if key not in errors.keys():
                    key = 'UNKNOWN'
                args[0] = {'detail': key}

            super(_ErrorSerializer, self).__init__(*args, **kwargs)

        detail = serializers.ChoiceField(help_text=f"Reason code for error, explanation:<br />"
                                                   f"{help}",
                                         choices=errors_lst)

    for key, val in errors.items():
        setattr(_ErrorSerializer, key, val)

    _ErrorSerializer.__name__ = name_cls

    return _ErrorSerializer
