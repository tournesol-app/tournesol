from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator
from rest_framework.serializers import EmailField
from rest_registration.api.serializers import (
    DefaultRegisterUserSerializer,
    DefaultRegisterEmailSerializer,
)

from core.models.user import User

RESERVED_USERNAMES = ["me"]


class RegisterUserSerializer(DefaultRegisterUserSerializer):
    # Temporary validator, to reject existing email on account creation.
    # The uniquessness will be enforced in the model, after the database
    # (and the dev datasets) have been cleaned up, and the migration can
    # be executed safely.
    email = EmailField(validators=[
        UniqueValidator(
            queryset=User.objects.all(),
            message="A user with this email address already exists."
        ),
    ])

    def validate_username(self, value):
        if value in RESERVED_USERNAMES:
            raise ValidationError(f'"{value}" is a reserved username')
        return value


class RegisterEmailSerializer(DefaultRegisterEmailSerializer):
    email = EmailField(validators=[
        UniqueValidator(
            queryset=User.objects.all(),
            message="A user with this email address already exists."
        ),
    ])
