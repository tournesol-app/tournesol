from abc import abstractmethod
from typing import Any, Callable
from numpy.typing import NDArray


class Minimizer:
    @abstractmethod
    def __call__(self, 
        init: NDArray, 
        args: tuple, 
        loss: Callable[[NDArray, Any], float] | None,
        gradient_function: Callable[[NDArray, Any], NDArray] | None,
        partial_derivative: Callable[[int, NDArray, Any], Callable[[float], float]] | None,
    ) -> NDArray:
        """ Minimizes loss. In loss, jac and partial_derivative, Any should be the *args.
        Note that some minimizers may only require some of these three functions. """

    @classmethod
    def load(cls, minimizer: tuple | list | dict | None = None, **kwargs) -> "Minimizer":
        if isinstance(minimizer, (tuple, list)):
            assert len(minimizer) == 2, minimizer
            clsname, minimizer_kwargs = minimizer
            assert isinstance(minimizer_kwargs, dict), minimizer_kwargs
            import solidago
            return getattr(solidago.primitives.minimizer, clsname)(**(minimizer_kwargs | kwargs))
        minimizer = minimizer or dict()
        minimizer = cls(**(minimizer | kwargs))
        assert isinstance(minimizer, Minimizer)
        return minimizer