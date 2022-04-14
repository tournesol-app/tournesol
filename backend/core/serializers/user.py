from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import BooleanField, EmailField
from rest_framework.validators import UniqueValidator
from rest_registration.api.serializers import (
    DefaultRegisterEmailSerializer,
    DefaultRegisterUserSerializer,
    DefaultUserProfileSerializer,
)
from rest_registration.utils.validation import wrap_validation_error_with_field

from core.models.user import User

RESERVED_USERNAMES = ["me"]


def _validate_username(value):
    if value in RESERVED_USERNAMES:
        raise ValidationError(_("'%(name)s' is a reserved username") % {"name": value})
    if value and "@" in value:
        raise ValidationError(_("'@' is not allowed in username"))
    return value


@wrap_validation_error_with_field("email")
def validate_email(value):
    try:
        User.objects.get(email__iexact=value.lower())
    except User.DoesNotExist:
        pass
    else:
        raise ValidationError("A user with this email address already exists.")


class RegisterUserSerializer(DefaultRegisterUserSerializer):
    def validate_username(self, value):
        return _validate_username(value)

    def validate(self, data):
        validate_email(data["email"])
        super(RegisterUserSerializer, self).validate(data)
        return data


class RegisterEmailSerializer(DefaultRegisterEmailSerializer):
    email = EmailField(
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="A user with this email address already exists.",
            ),
        ]
    )


class UserProfileSerializer(DefaultUserProfileSerializer):
    is_trusted = BooleanField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        extra_fields = ("is_trusted",)
        self.Meta.fields += extra_fields
        self.Meta.read_only_fields += extra_fields

    def validate_username(self, value):
        return _validate_username(value)
