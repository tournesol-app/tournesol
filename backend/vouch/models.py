from django.db import models
from django.db.models import ObjectDoesNotExist
from core.models.user import User

class Vouch(models.Model)

    vouching = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="",
        related_name="vouchinguser",
    )
    vouchedfor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="The contributor",
        related_name="vouchedforuser",
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
        if not self._state.adding and (
            self.creator_id != self._loaded_values['creator_id']):
         raise ValueError("Updating the value of creator isn't allowed")
        super().save(*args, **kwargs)

    def get_vouchedfor(vouching):
        try:
            vouching = vouch.objects.get(vouching = vouching)
        except ObjectDoesNotExist:
            pass
        else:
            return vouching, False
        vouching = vouch.objects.get(vouching = vouching)
        return vouching, True

    def get_vouching(vouchedfor):
        try:
            vouchedfor = vouch.objects.filter(vouchedfor = vouchedfor)
        except ObjectDoesNotExist:
            pass
        else:
            return vouchedfor, False
        vouchedfor = vouch.objects.filter(vouchedfor = vouchedfor)
        return vouchedfor, True


    

