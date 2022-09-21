"""
Models related to the vouching system.
"""

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models.user import User


class Voucher(models.Model):
    """A `Voucher` given by a user to another one.

    A `Voucher` represents a mark of trust a user is able to grant to another
    user. Each mark of trust has a trust value.

    These vouchers can be used by an algorithm to compute the global trust
    score given to every user by the network, in order to weight their voting
    right accordingly.
    """

    by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="The user giving the voucher.",
        related_name="vouchers_given",
    )
    to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="The user receiving the voucher.",
        related_name="vouchers_received",
    )
    is_public = models.BooleanField(
        default=True, help_text="Should the voucher be public?"
    )
    value = models.FloatField(
        default=1,
        help_text="The vouch value given by the vouching user to receiving user.",
    )

    class Meta:
        unique_together = ["by", "to"]

    @staticmethod
    def get_given_by(user):
        vouchers = Voucher.objects.filter(by=user)
        return vouchers, vouchers.exists()

    @staticmethod
    def get_given_to(user):
        vouchers = Voucher.objects.filter(to=user)
        return vouchers, vouchers.exists()

    def clean(self):
        if self.by == self.to:
            raise ValidationError(_("A user cannot vouch for himself."))

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValueError("Updating a voucher is not allowed.")
        super().save(*args, **kwargs)
