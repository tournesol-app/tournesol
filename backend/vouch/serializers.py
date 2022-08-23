from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from core.models import User
from vouch.models import Voucher


# Allow to keep the JSON representation of `GivenVoucherSerializer` and
# `ReadOnlyVoucherSerializer` similar.
VOUCHER_FIELDS = ["by", "to", "is_public", "value"]


class GivenVoucherSerializer(ModelSerializer):
    """
    A voucher given by the logged-in user to a target user.

    As the public status of the voucher is displayed, this serializer
    shouldn't be used to list the vouchers not related to the logged-in user.
    Prefer `PublicGivenVoucherSerializer` instead.
    """

    by = serializers.CharField(default=serializers.CurrentUserDefault())
    to = serializers.CharField()

    class Meta:
        model = Voucher
        fields = VOUCHER_FIELDS
        read_only_fields = ["by"]

    def validate_to(self, value):
        try:
            user = User.objects.get(username=value)
        except User.DoesNotExist as error:
            raise ValidationError(_("The target user doesn't exist.")) from error

        return user

    def validate(self, attrs):
        if attrs["by"] == attrs["to"]:
            raise serializers.ValidationError(
                {"to": _("You cannot vouch for yourself.")}
            )
        return attrs


class ReadOnlyVoucherSerializer(ModelSerializer):
    """
    A read-only `Voucher` serializer.

    Can be used to safely display a given or a received voucher.

    As the public status of the voucher is displayed, this serializer
    shouldn't be used to list the vouchers not related to the logged-in user.
    Prefer `PublicReadOnlyVoucherSerializer` instead.
    """

    by = serializers.CharField()
    to = serializers.CharField()

    class Meta:
        model = Voucher
        fields = VOUCHER_FIELDS
        read_only_fields = ["to", "by", "is_public", "value"]
