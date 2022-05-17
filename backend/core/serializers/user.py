from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import BooleanField, EmailField
from rest_framework.validators import UniqueValidator
from rest_registration.api.serializers import (
    DefaultRegisterEmailSerializer,
    DefaultRegisterUserSerializer,
    DefaultSendResetPasswordLinkSerializer,
    DefaultUserProfileSerializer,
)
from rest_registration.utils.users import (
    get_user_by_lookup_dict,
    get_user_login_field_names,
)


from core.models.user import User

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

    def validate_email(self, value):
        return User.validate_email_unique_with_plus(value)


class RegisterEmailSerializer(DefaultRegisterEmailSerializer):
    email = iunique_email

    def validate_email(self, value):
        return User.validate_email_unique_with_plus(
            value, self.context["request"].user.username
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


class SendResetPasswordLinkSerializer(DefaultSendResetPasswordLinkSerializer):
    """
    Custom overload of the serializer used for sending reset password link.

    Contrary to REST Registration's `DefaultSendResetPasswordLinkSerializer`,
    this class is able to use any Django field lookups to retrieve the user.

    It allows us to retrieve users with a non-case-sensitive email.
    """
    _lookups = {"email": "email__iexact"}

    def get_user_or_none(self):
        validated_data = self.context["request"].data

        login_field_names = get_user_login_field_names()
        finder_tests = [("login", login_field_names)]
        finder_tests.extend((f, [f]) for f in login_field_names)

        for field_name, db_field_names in finder_tests:
            value = validated_data.get(field_name)
            if value is None:
                continue
            for db_fn in db_field_names:

                lookup_field = self._lookups.get(db_fn)
                if not lookup_field:
                    lookup_field = db_fn

                user = get_user_by_lookup_dict(
                    {lookup_field: value}, default=None, require_verified=False
                )
                if user is not None:
                    return user

        return None
