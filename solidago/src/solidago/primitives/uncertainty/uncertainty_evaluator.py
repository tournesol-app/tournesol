from abc import abstractmethod
from typing import Callable, Any
from numpy.typing import NDArray


class UncertaintyEvaluator:
    @abstractmethod
    def __call__(self, 
        values: NDArray, 
        args: tuple,
        translated_loss: Callable[[int, NDArray, Any], Callable[[float], float]] | None = None,
        translated_prior: Callable[[int, NDArray, Any], Callable[[float], float]] | None = None,
        hess_diagonal: Callable[[NDArray, Any], NDArray] | None = None,
    ) -> tuple[NDArray, NDArray]:
        """ Minimizes loss. In loss, jac and partial_derivative, Any should be the *args.
        Note that some minimizers may only require some of these three functions. """

    @classmethod
    def load(cls, uncertainty: tuple | list | dict | None = None, **kwargs) -> "UncertaintyEvaluator":
        if isinstance(uncertainty, (tuple, list)):
            assert len(uncertainty) == 2, uncertainty
            clsname, uncertainty_kwargs = uncertainty
            assert isinstance(uncertainty_kwargs, dict), uncertainty_kwargs
            import solidago
            return getattr(solidago.primitives.uncertainty, clsname)(**(uncertainty_kwargs | kwargs))
        uncertainty = uncertainty or dict()
        uncertainty = cls(**(uncertainty | kwargs))
        assert isinstance(uncertainty, UncertaintyEvaluator)
        return uncertainty