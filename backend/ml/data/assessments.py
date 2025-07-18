import solidago


class Assessments(solidago.Assessments):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def load(cls, poll_name: str, *args, **kwargs) -> "Assessments":
        return cls(*args, **kwargs)

    def save(self, poll_name: str, name: str="assessments", **kwargs) -> tuple[str, dict]:
        # Solidago must not modify assessments
        raise NotImplemented
