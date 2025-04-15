import solidago


class Assessments(solidago.Assessments):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def load(cls, directory: str, *args, **kwargs) -> "Assessments":
        return cls(*args, **kwargs)

    def save(self, directory: str, name: str="assessments", **kwargs) -> tuple[str, dict]:
        # Solidago must not modify assessments
        raise NotImplemented
