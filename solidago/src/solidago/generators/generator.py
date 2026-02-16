from solidago.poll import Poll
from solidago.poll_functions import Sequential, PollFunction


class Generator(Sequential):
    def __init__(self, modules: list | None = None, max_workers: int | None = None, seed: int | None = None):
        super().__init__(name="Generator", max_workers=max_workers, seed=seed)
        from solidago import generators
        def load(module):
            if isinstance(module, PollFunction):
                return module
            assert isinstance(module, (tuple, list)) and len(module) == 2, module
            classname, kwargs = module
            classnames = classname.split(".")
            cls = generators
            for name in classnames:
                cls = getattr(cls, name)
            assert isinstance(cls, type), cls
            return getattr(cls, "load")(**kwargs) if hasattr(cls, "load") else cls(**kwargs)
        self.modules: list[PollFunction] = [load(m) for m in modules or list()]
 

