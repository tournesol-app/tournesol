import numpy as np

from solidago.poll import Poll
from solidago.functions import Sequential, PollFunction


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
            return cls.load(**kwargs) if hasattr(cls, "load") else cls(**kwargs)
        self.modules: list[PollFunction] = [load(m) for m in modules or list()]
 
    def __call__(self, poll: Poll | None = None, save_directory: str | None = None, skip_steps: set={}) -> Poll:
        return super().__call__(poll or Poll(), save_directory, skip_steps)


class GeneratorStep(PollFunction):
    def __repr__(self, n_indents: int = 0):
        def sub_repr(key):
            value = getattr(self, key)
            if key == "modules":
                return ", ".join([v.__repr__(n_indents + 1) for v in value])
            return value.__repr__(n_indents + 1) if isinstance(value, PollFunction) else value

        indent = "\t" * (n_indents + 1)
        last_indent = "\t" * n_indents
        t = ".".join(str(type(self)).split(".")[2:])[:-2]
        return f"{t}(\n{indent}" + f",\n{indent}".join([
            f"{key}={sub_repr(key)}"  for key in self.yaml_keys()
        ]) + f"\n{last_indent})"