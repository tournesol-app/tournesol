import base64
import datetime
import imghdr
import uuid
from contextlib import contextmanager

import six
from backend.models import UserPreferences, Video
from django.core.files.base import ContentFile
from django.http import Http404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import extend_schema_field
from django.core.exceptions import ValidationError as ModelValidationError
from rest_framework import serializers
from .error_serializer import error_serializer
from backend.rating_fields import VIDEO_FIELDS
from backend.rating_fields import MAX_VALUE as MAX_RATING


# common errors
GenericErrorSerializer = error_serializer("Generic")


def video_get_or_create_verify_raise(field=None, **kwargs):
    """Either get a video, or create one. On errors, raise serializers.ValidationError."""
    try:
        v = Video.get_or_create_with_validation(**kwargs)
        return v
    except ModelValidationError as e:
        if field is None:
            raise serializers.ValidationError(e.message_dict)
        else:
            raise serializers.ValidationError({field: e.message_dict})


def get_user_preferences(request):
    """Get user preferences given a request."""
    return UserPreferences.objects.get(user__username=request.user.username)


def filter_date_ago(queryset, field_name, value, lookup_expr=None):
    """Search over a date field, converted into 'days ago' in an efficient way."""
    time_threshold = datetime.datetime.now() - datetime.timedelta(days=float(value))
    f = '__'.join([field_name, lookup_expr])
    return queryset.filter(**{f: time_threshold})


def identity(queryset, *args, **kwargs):
    """Return the queryset."""
    return queryset


def pretty_time_delta(seconds):
    """Print seconds as 'time delta' ago."""
    seconds = int(seconds)
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    if days > 0:
        return '%dd' % days
    elif hours > 0:
        return '%dh' % hours
    elif minutes > 0:
        return '%dm' % minutes
    else:
        return '%ds' % (seconds,)


def WithUpdatedDocstringsDecorator(
        cls,
        docstring_dict='UPDATE_DOCSTRING',
        kwargs_dict='KWARGS_DICT'):
    """Set docs on API methods ia @extend_schema."""
    if not hasattr(cls, docstring_dict):
        raise ValueError(
            f"Attribute {docstring_dict} not found in class {cls}")

    docs = getattr(cls, docstring_dict)
    kwargs_dict = getattr(cls, kwargs_dict, {})

    for key, value in docs.items():
        if key not in kwargs_dict:
            kwargs_dict[key] = {}
        kwargs_dict[key]['description'] = value

    for k, v in kwargs_dict.items():
        if not hasattr(cls, k):
            raise ValueError(f"Method {k} not found in class {cls}")

        old_f = getattr(cls, k)

        def new_fcn(*args, old_f=old_f, **kwargs):
            return old_f(*args, **kwargs)

        new_fcn.__name__ = old_f.__name__
        setattr(cls, k, extend_schema(**v)(new_fcn))

    return cls


def remove_v1_api_hook(endpoints):
    """Only keep api v2."""
    new_endpoints = []
    for (path, path_regex, method, callback) in endpoints:
        if path.startswith('/api/v2'):
            new_endpoints.append((path, path_regex, method, callback))
    return new_endpoints


@contextmanager
def change_user_data(querydict):
    """'Unlock' a querydict."""
    if hasattr(querydict, '_mutable'):
        querydict._mutable = True
    yield
    if hasattr(querydict, '_mutable'):
        querydict._mutable = False


class WithPKOverflowProtection(object):
    def get_object(self):
        """If got an overflow error because the pk is invalid, return 404."""
        try:
            return super(WithPKOverflowProtection, self).get_object()
        except OverflowError:
            raise Http404


class WithNestedWritableFields(object):
    """Support nested fields in update/create"""

    # FORMAT: {field name(str) -> serializer class}
    # Meta.nested_fields = {}
    # Meta = None

    def set_updated_fields(self, instance, validated_data):
        """Set values for nested fields based on NESTED FIELDS attribute."""

        errors = {}
        updated_data = {}

        # pre-processing data
        for key, s in self.Meta.nested_fields.items():
            # obtaining the attribute
            data_list = validated_data.get(key, None)

            # saving data if it exists
            if data_list is not None:
                # preprocessing data
                for i in range(len(data_list)):
                    f = self.Meta.nested_preprocess.get(key, lambda x: x)
                    data_list[i] = f(data_list[i])

            updated_data[key] = data_list

        # validating data
        for key, s in self.Meta.nested_fields.items():
            data_list = updated_data[key]
            if data_list is not None:
                # validating data
                for i, data in enumerate(data_list):
                    ser = s(data=data)
                    if not ser.is_valid(raise_exception=False):
                        if key not in errors:
                            errors[key] = {}
                        errors[key][i] = ser.errors

        if not errors:
            for key, s in self.Meta.nested_fields.items():
                data_list = updated_data[key]
                if data_list is not None:
                    # creating/obtaining objects
                    objects = [
                        s.Meta.model.objects.get_or_create(
                            user=instance,
                            **data)[0] for data in data_list]

                    # setting data
                    getattr(instance, key).set(objects)

                    # setting rank
                    for i, obj in enumerate(objects, start=1):
                        setattr(obj, 'rank', i)
                        obj.save()
        else:
            raise serializers.ValidationError(errors)

        return instance

    def update(self, instance, validated_data):
        """Update instance with support of nested fields."""
        for key, val in validated_data.items():
            if key not in self.Meta.nested_fields:
                setattr(instance, key, val)
        instance.save()

        return self.set_updated_fields(instance, validated_data)

    def create(self, validated_data):
        """Create an instance with support of nested fields."""
        instance = self.Meta.model.objects.create(
            **{x: y for x, y in validated_data.items() if x not in self.Meta.nested_fields})
        return self.set_updated_fields(instance, validated_data)


class Base64ImageField(serializers.ImageField):
    """Support data-url encoding in ImageField uploads.

    Source: https://stackoverflow.com/questions/31690991/uploading-base64-
        images-using-modelserializers-in-django-django-rest-framework
    """

    def get_file_extension(self, file_name, decoded_file):
        """Guess file extension from the content."""

        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension

        return extension

    def to_internal_value(self, data):
        """Decode base64 into an image."""
        if isinstance(data, six.string_types):
            # base64 encoding means that we decode it
            if 'data:' in data and ';base64,' in data:
                header, data = data.split(';base64,')

                try:
                    decoded_file = base64.b64decode(data)
                except TypeError:
                    self.fail('invalid_image')

                fn = 'filename='
                # assume filename is last
                if fn in header:
                    i = header.index(fn)
                    file_name = header[i + len(fn):]
                    complete_file_name = file_name
                else:
                    # 12 characters are more than enough.
                    file_name = str(uuid.uuid4())[:12]
                    file_extension = self.get_file_extension(
                        file_name, decoded_file)
                    complete_file_name = "%s.%s" % (
                        file_name, file_extension,)
                data = ContentFile(decoded_file, name=complete_file_name)

        return super(Base64ImageField, self).to_internal_value(data)


@extend_schema_field(OpenApiTypes.STR)
class MarkerField(serializers.ReadOnlyField):
    """Add a a tag displaying something in the form."""

    def __init__(self):
        super(
            MarkerField,
            self).__init__(
            default="",
            help_text="Marker",
            required=False)


class HashIDStorage(object):
    """Store strings and return their IDs."""

    def __init__(self):
        self.reset()

    def reset(self):
        # format: object id -> subobject id -> index
        self.storage = {}

    def add(self, obj, item):
        """Add an item, returns the index."""
        if obj not in self.storage:
            self.storage[obj] = {}

        if item not in self.storage[obj]:
            self.storage[obj][item] = len(self.storage[obj])

        return self.index(obj, item)

    def index(self, obj, item):
        """Return an index of an item or -1."""
        return self.storage.get(obj, {}).get(item, -1)


def update_preferences_vector_from_request(vector, request_query_params):
    """Given a preferences vector, update values from a given dictionary."""
    # trying the override
    for i, k in enumerate(VIDEO_FIELDS):
        if k in request_query_params:
            try:
                vector[i] = float(
                    request_query_params[k]) - MAX_RATING / 2
            except ValueError as e:
                raise serializers.ValidationError({k: [f'Wrong value, {str(e)}']})
    return vector
