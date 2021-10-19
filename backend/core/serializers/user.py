from rest_framework.exceptions import ValidationError
from rest_registration.api.serializers import DefaultRegisterUserSerializer

RESERVED_USERNAMES = ["me"]


class RegisterUserSerializer(DefaultRegisterUserSerializer):
    def validate_username(self, value):
        if value in RESERVED_USERNAMES:
            raise ValidationError(f'"{value}" is a reserved username')
        return value
