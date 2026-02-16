from abc import abstractmethod
from typing import Callable, Any, Self
from numpy.typing import NDArray

import numpy as np


_LoadableType = type | str | tuple[str | type, dict[str, Any]] | list[str | type | dict[str, Any]] | dict[str, Any]

# CwLossGetter retrieves a coordinate-wise loss function, which may depend on a coordinate
CwLossGetter = Callable[
    [NDArray[np.float64], *tuple[Any, ...]], 
    tuple[
        Callable[[float, np.int64, *tuple[Any, ...]], float], # cw_loss
        tuple[Any, ...] # cw_loss_args
    ]
]

class UncertaintyEvaluator:
    @abstractmethod
    def __call__(self, 
        values: NDArray[np.float64], 
        args: tuple[Any, ...],
        cw_prior_loss_getter: CwLossGetter | None = None,
        cw_nll_loss_getter: CwLossGetter | None = None,
        hess_diagonal: Callable[[NDArray[np.float64], *tuple[Any, ...]], NDArray[np.float64]] | None = None,
    ) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
        """ Minimizes loss. In loss, jac and partial_derivative, Any should be the *args.
        Note that some minimizers may only require some of these three functions. """

    @classmethod
    def load(cls, arg: _LoadableType | Self | None = None, **kwargs: Any) -> "UncertaintyEvaluator":
        if isinstance(arg, UncertaintyEvaluator):
            return arg
        import solidago
        s = solidago.load(arg or dict(), solidago.primitives.minimizer, **kwargs)
        assert isinstance(s, UncertaintyEvaluator)
        return s


def to_cw_loss_getter(loss: Callable[[NDArray, *tuple[Any, ...]], float]) -> CwLossGetter:
    def cw_loss_getter(values: NDArray[np.float64], *args: Any) -> tuple[
        Callable[[float, np.int64, *tuple[Any, ...]], float], 
        tuple[Any, ...]
    ]:
        def cw_loss(delta: float, index: np.int64, values: NDArray, *args) -> float:
            base_vector = np.zeros_like(values)
            base_vector[index] = 1
            return loss(values + delta * base_vector, *args)
        return cw_loss, (values, *args)
    return cw_loss_getter
