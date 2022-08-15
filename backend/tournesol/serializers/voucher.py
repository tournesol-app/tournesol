from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from core.models import User
from vouch.models import Voucher


class VoucherSerializer(ModelSerializer):
    by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    to = serializers.CharField()

    class Meta:
        model = Voucher

        fields = [
            "id",
            "by",
            "to",
            "is_public",
            "value",
        ]

    def validate_to(self, value):
        try:
            user = User.objects.get(username=value)
        except User.DoesNotExist as error:
            raise ValidationError("The target user doesn't exist.") from error

        return user

    def validate(self, attrs):
        if attrs["by"] == attrs["to"]:
            raise serializers.ValidationError({"to": "You cannot vouch for yourself"})
        return attrs
