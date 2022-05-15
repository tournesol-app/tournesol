from django.db import models

from core.models.user import User



class Voucher(models.Model):
    """A `Voucher` given by a user to another one.
    A `Voucher` represents a mark of trust related to a specific attribute (PoP, degree, diploma, ...)
    a user is able to grant to another one. Each mark of trust has a
    trust value and an associated uncertainty to weight its effect.
    These vouchers can be used by an algorithm to compute the global trust score given to every user by the
    network, in order to weight their voting right accordingly.
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
        default=False, help_text="Should the voucher be public?"
    )
    trust_value = models.FloatField(
        default=0,
        help_text="The trust value given by the vouching user to receiving user.",
    )
    # XXX: What is the vouching score described in the help text? Is it the
    # `trust_value`? If yes we should use the same vocabulary to avoid any
    # confusion.
    uncertainty = models.FloatField(
        default=0,
        help_text="Uncertainty about the voucher score.",
    )
    attribute = models.TextField(
        max_length=32,
        help_text="Name of the attribute corresponding to this voucher.",
        db_index=True,
    )
    @staticmethod
    def get_given_to(user):
        vouchers = Voucher.objects.filter(to=user)
        return vouchers, vouchers.exists()

    @staticmethod
    def get_received_by(user):
        vouchers = Voucher.objects.filter(by=user)
        return vouchers, vouchers.exists()

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValueError("Updating a voucher is not allowed.")
        super().save(*args, **kwargs)