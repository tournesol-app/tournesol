from solidago.poll_functions import Sequential, PollFunction


class Generator(Sequential):
    def __init__(self, subfunctions: list | None = None, max_workers: int | None = None, seed: int | None = None):
        super().__init__(name="Generator", max_workers=max_workers, seed=seed)
        import solidago
        self.subfunctions: list[PollFunction] = [solidago.load(f, solidago.generators) for f in subfunctions or list()]
 

