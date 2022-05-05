from django.db import models
from django.db.models import ObjectDoesNotExist
from core.models.user import User


class Vouch(models.Model):
    by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="User who vouch for",
        related_name="user_by",
        default= 0,
    )
    to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="User being vouched for",
        related_name="user_to",
        default= 0,
    )
    is_public = models.BooleanField(
        default=False, help_text="Should the vouching be public?"
    )

    trust_value = models.FloatField(
        default=0,
        help_text="Trust value assigned by vouching user to vouched-for user.",
    )
    uncertainty = models.FloatField(
        default=0,
        help_text="Uncertainty about the vouching score",
    )
    criteria = models.TextField(
        default=0,
        max_length=32,
        help_text="Name of the properity on which the vouching is based",
        db_index=True,
    )

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValueError("This vouching is not allowed")
        super().save(*args, **kwargs)

    @staticmethod

    def get_to(by):
        to = Vouch.objects.filter(by = by)
        return to, to.exists()

    @staticmethod
    def get_by(to):
        by = Vouch.objects.filter(to = to)
        return by, by.exists()