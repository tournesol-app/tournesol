from rest_framework.exceptions import ValidationError
from rest_framework.serializers import BooleanField, EmailField
from rest_framework.validators import UniqueValidator
from rest_registration.api.serializers import (
    DefaultRegisterEmailSerializer,
    DefaultRegisterUserSerializer,
    DefaultUserProfileSerializer,
)

from core.models.user import User

RESERVED_USERNAMES = ["me"]


class RegisterUserSerializer(DefaultRegisterUserSerializer):
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


class UserProfileSerializer(DefaultUserProfileSerializer):
    is_trusted = BooleanField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        extra_fields = ('is_trusted',)
        self.Meta.fields += extra_fields
        self.Meta.read_only_fields += extra_fields
