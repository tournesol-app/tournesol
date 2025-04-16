import solidago


DEFAULT_CLS_MODEL = ("SquashedModel", {
    "note": "squash",
    "score_max": 100,
    "parent": ["DirectScoring", { "note": "average" }],
    "directs": { "keynames": ["entity_name", "criterion"] }
})

class SquashedGlobalModel(solidago.Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def load(cls, directory: str, cls_model: tuple=DEFAULT_CLS_MODEL, *args, **kwargs) -> "GlobalModel":
        for name in ("directs", "scales"):
            if name not in kwargs:
                continue
            try:
                filename = f"{directory}/{kwargs[name]['name']}"
                init_data = pd.read_csv(filename, keep_default_na=False)
            except (pd.errors.EmptyDataError, ValueError):
                init_data = None
            kwargs[name] = MultiScore(kwargs[name]["keynames"], init_data)
        return cls(**kwargs)

    def save(self, directory: Optional[str]=None, json_dump: bool=False) -> tuple[str, dict]:
        """ save must be given a filename_root (typically without extension),
        as multiple csv files may be saved, with a name derived from the filename_root
        (in addition to the json description) """
        for table_name in ("directs", "scales"):
            table = getattr(self, f"get_{table_name}")()
            if table:
                table.save(directory, f"{table_name}.csv")
        return self.save_instructions(directory, json_dump)