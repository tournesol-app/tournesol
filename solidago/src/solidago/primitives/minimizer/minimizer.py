from abc import abstractmethod
from typing import Any, Callable, Self
from numpy.typing import NDArray

import numpy as np


_LoadableType = type | str | tuple[str | type, dict[str, Any]] | list[str | type | dict[str, Any]] | dict[str, Any]

class Minimizer:
    @abstractmethod
    def __call__(self, 
        init: NDArray[np.float64], 
        args: tuple[Any, ...] = (), 
        loss: Callable[[NDArray[np.float64], *tuple[Any, ...]], float] | None = None,
        gradient_function: Callable[[NDArray[np.float64], *tuple[Any, ...]], NDArray[np.float64]] | None = None,
        partial_derivative: Callable[[int, NDArray[np.float64], *tuple[Any, ...]], Callable[[float, *tuple[Any, ...]], float]] | None = None,
    ) -> NDArray[np.float64]:
        """ Minimizes loss. In loss, jac and partial_derivative, Any should be the *args.
        Note that some minimizers may only require some of these three functions. """

    @classmethod
    def load(cls, minimizer: _LoadableType | Self | None = None, **kwargs: Any) -> "Minimizer":
        if isinstance(minimizer, Minimizer):
            return minimizer
        import solidago
        m = solidago.load(minimizer or dict(), solidago.primitives.minimizer, **kwargs)
        assert isinstance(m, Minimizer)
        return m