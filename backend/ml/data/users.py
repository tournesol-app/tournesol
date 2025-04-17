from django.db.models import F, Q
from pandas import DataFrame

from core.models import User
import solidago


class Users(solidago.Users):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def load(cls, *args, **kwargs) -> "Users":
        values = (
            User.objects
            .filter(is_active=True)
            .annotate(is_pretrusted=Q(pk__in=User.with_trusted_email()))
            .values(
                "is_pretrusted",
                trust=F("trust_score"),
                username=F("id"),
            )
        )
        init_data = DataFrame(
            data=values,
            columns=["username", "is_pretrusted", "trust_score"],
        ).set_index("username")
        return Users(init_data, *args, **kwargs)

    def save(self, name: str="users", **kwargs) -> tuple[str, dict]:
        """ TODO: Should be able to export any columns, e.g. 'is_scaler_largely_recommended' """
        django_users = User.objects.filter(id__in=self.keys()).only("trust_score")
        for solidago_user, django_user in zip(self, django_users):
            django_user.trust_score = solidago_user.trust
        User.objects.bulk_update(
            django_user,
            ["trust_score"],
            batch_size=1000
        )
        return self.save_instructions(name)
