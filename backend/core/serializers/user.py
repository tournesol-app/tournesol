from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import BooleanField, EmailField
from rest_framework.validators import UniqueValidator
from rest_registration.api.serializers import (
    DefaultRegisterEmailSerializer,
    DefaultRegisterUserSerializer,
    DefaultUserProfileSerializer,
)

from core.models.user import User
from core.validators import validate_email_localpart_noplus

RESERVED_USERNAMES = ["me"]

iunique_email = EmailField(
    validators=[
        UniqueValidator(
            queryset=User.objects.all(),
            message=_("A user with this email address already exists."),
            lookup="iexact",
        ),
    ]
)


def _validate_username(value):
    if value in RESERVED_USERNAMES:
        raise ValidationError(_("'%(name)s' is a reserved username") % {"name": value})
    if value and "@" in value:
        raise ValidationError(_("'@' is not allowed in username"))
    return value


class RegisterUserSerializer(DefaultRegisterUserSerializer):
    email = iunique_email

    def validate_username(self, value):
        return _validate_username(value)


    def validate(self, data):
        validate_email_localpart_noplus(data["email"])
        return data


class RegisterEmailSerializer(DefaultRegisterEmailSerializer):
    email = iunique_email

    def validate(self, data):
        validate_email_localpart_noplus(
            data["email"],
            self.context["request"].user.username
        )
        return data


class UserProfileSerializer(DefaultUserProfileSerializer):
    is_trusted = BooleanField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        extra_fields = ("is_trusted",)
        self.Meta.fields += extra_fields
        self.Meta.read_only_fields += extra_fields

    def validate_username(self, value):
        return _validate_username(value)
