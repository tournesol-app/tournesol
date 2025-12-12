import numpy as np
import logging

from solidago.poll import Poll
from solidago.modules import Sequential, PollFunction

logger = logging.getLogger(__name__)


class Generator(Sequential):
    def __init__(self, modules: list | None = None, max_workers: int | None = None):
        super().__init__(None, max_workers=max_workers)
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
 
    def __call__(self, poll: Poll | None = None, seed: int | None = None) -> Poll:
        """ Generates a random dataset, presented as a poll.
        No processing of the dataset is performed by the generative model.
        
        Parameters
        ----------
        poll: Poll or None
            Optional poll to derive computations from
        seed: None or int
            If int, sets numpy ranom seed for reproducibility
            
        Returns
        -------
        poll: Poll
        """
        if seed is not None:
            assert type(seed) == int
            np.random.seed(seed)

        return super().__call__(poll or Poll())


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