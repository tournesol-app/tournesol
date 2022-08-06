from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer
from rest_framework.validators import UniqueTogetherValidator

from core.models import User
from vouch.models import Voucher


class VoucherSerializer(ModelSerializer):
    by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    to = serializers.CharField()

    class Meta:
        model = Voucher

        fields = [
            "by",
            "to",
            "is_public",
            "value",
        ]

        validators = [
            UniqueTogetherValidator(
                queryset=Voucher.objects.all(),
                fields=["to", "by"],
            )
        ]

    def validate_to(self, value):
        try:
            user = User.objects.get(username=value)
        except User.DoesNotExist as error:
            raise ValidationError("The target user doesn't exist.") from error

        return user
