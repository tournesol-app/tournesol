from solidago.primitives.datastructures import Objects


class Users(Objects):
    VALUE_NAMES = ["username", "is_pretrusted", "trust"]

    @classmethod
    def range(cls, n: int, vector_dims=0):
        return cls.from_dict(
            {(idx,): ("", False, 0.0) for idx in range(n)},
            sparse=False,
            vector_dims=vector_dims,
        )

    @classmethod
    def from_usernames(cls, usernames: list[str]):
        return cls.from_dict({
            (username,): (username, False, 0.0)
            for username in usernames
        })

    @classmethod
    def load(cls, directory: str, name: str, id_column: str | None = "username"):
        return super().load(directory=directory, name=name, id_column=id_column)
        