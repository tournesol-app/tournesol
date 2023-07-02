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
from core.serializers.user_settings import TournesolUserSettingsSerializer

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
    settings = TournesolUserSettingsSerializer(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Meta.read_only_fields += ("trust_score",)

    def validate_username(self, value):
        return _validate_username(value)

    def validate_email(self, value):
        return User.validate_email_unique_with_plus(value)


class RegisterEmailSerializer(DefaultRegisterEmailSerializer):
    email = iunique_email

    def validate_email(self, value):
        return User.validate_email_unique_with_plus(
            value, self.context["request"].user.username
        )


class UserProfileSerializer(DefaultUserProfileSerializer):
    is_trusted = BooleanField(read_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Default writable fields are defined in setting REST_REGISTRATION.USER_EDITABLE_FIELDS
        extra_fields = ("is_trusted",)
        self.Meta.fields += extra_fields
        self.Meta.read_only_fields += extra_fields

    def validate_username(self, value):
        return _validate_username(value)
