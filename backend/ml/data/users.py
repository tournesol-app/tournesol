import solidago


class Users(solidago.Users):
    def __init__(self, *args, **kwargs):
        super().__init__(data=self.query_init_data(), *args, **kwargs)

    def query_init_data(self):
        values = (
            User.objects
            .filter(is_active=True)
            .annotate(is_pretrusted=Q(pk__in=User.with_trusted_email()))
            .values(
                "is_pretrusted",
                "trust_score",
                username=F("id"),
            )
        )
        return pd.DataFrame(
            data=values,
            columns=["username", "is_pretrusted", "trust_score"],
        ).set_index("username")
