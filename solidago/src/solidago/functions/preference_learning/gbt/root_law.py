from abc import abstractmethod
from typing import Union
from numpy.typing import NDArray
from numba import njit

import numpy as np

from solidago.poll import *


class RootLaw:
    def normalize_rating(self, rating: Rating) -> float:
        return float(rating.value)
    
    def normalize_comparison(self, comparison: Comparison) -> float:
        return float(comparison.value)

    @abstractmethod
    def sup(self) -> float:
        """ Supremum on the set of allowed value_diff. Also equals sup of cgf_derivative, see Theorem 1 of
        "Generalized Bradley-Terry Models for Score Estimation from Paired Comparisons" 
        by Julien Fageot, Sadegh Farhadkhani, Lê-Nguyên Hoang and Oscar Villemaud (AAAI'24). """

    def inf(self) -> float:
        return - self.sup()

    @abstractmethod
    def cgf(self, score_diffs: NDArray) -> NDArray:
        """ The cumulant-generating function is useful to compute the uncertainty,
        especially if we use uncertainties by increase of the negative log-likelihood.
        It may also be used by the optimizer to compute MAP values """
        
    @abstractmethod
    def cgf_derivative(self, score_diffs: NDArray) -> NDArray:
        """ The cumulant-generating function derivative is very useful 
        for optimization to compute the MAP values """
        
    @abstractmethod
    def cgf_2nd_derivative(self, score_diffs: NDArray) -> NDArray:
        """ The cumulant-generating function second derivative may be useful 
        for optimization uncertainty evaluation """
    
    @classmethod
    def load(cls, arg: tuple[str, dict] | None = None, default: Union["RootLaw", None] = None) -> "RootLaw":
        if arg is None:
            assert default is not None
            return default
        if isinstance(arg, RootLaw):
            return arg
        clsname, kwargs = arg
        kwargs = kwargs or dict()
        assert clsname in globals(), f"{clsname} must be the name of a root law"
        cls = globals()[clsname]
        assert issubclass(cls, RootLaw)
        return cls(**kwargs)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({', '.join([f'{k}={v}' for k, v in self.__dict__.items()])})"


class BradleyTerry(RootLaw):
    def normalize_rating(self, rating: Rating) -> float:
        mean = (rating.min + rating.max) / 2
        mean = 0 if np.isfinite(mean) else mean
        return np.sign(rating.value - mean)
    
    def normalize_comparison(self, comparison: Comparison) -> float:
        return np.sign(comparison.value)
    
    def sup(self) -> float:
        return 1.0

    def cgf(self, score_diffs: NDArray) -> NDArray:
        """ The cgf of UniformGBT is simply log( cosh(value_diff) ).
        However, numerical accuracy requires care when abs(value_diff) is large.
        """
        score_diffs_abs = np.abs(score_diffs)
        with np.errstate(all='ignore'):
            return np.where(
                score_diffs_abs < 20.0,
                np.log(np.cosh(score_diffs)),
                score_diffs_abs - np.log(2),
            )
        
    def cgf_derivative(self, score_diffs: NDArray) -> NDArray:
        return np.tanh(score_diffs)
    
    def cgf_2nd_derivative(self, score_diffs: NDArray) -> NDArray:
        return 1 / np.cosh(score_diffs)**2


class Uniform(RootLaw):
    def normalize_rating(self, rating: Rating) -> float:
        middle = (rating.max + rating.min) / 2
        return float(2 * (rating.value - middle) / (rating.max - rating.min))
    
    def normalize_comparison(self, comparison: Comparison) -> float:
        return float(comparison.value / comparison.max)
    
    def sup(self) -> float:
        return 1.0
    
    def cgf(self, score_diffs: NDArray) -> NDArray:
        """ The cgf of UniformGBT is simply log( sinh(value_diff) / value_diff ).
        However, numerical accuracy requires care when abs(value_diff) is small 
        (because of division by zero) or large (because sinh explodes).
        We use series expansion approximation for these cases.
        """
        score_diffs_abs = np.abs(score_diffs)
        with np.errstate(all='ignore'):
            return np.where(
                score_diffs_abs > 1e-1,
                np.where(
                    score_diffs_abs < 20.0,
                    np.log(np.sinh(score_diffs) / score_diffs),
                    score_diffs_abs - np.log(2) - np.log(score_diffs_abs),
                ),
                score_diffs_abs ** 2 / 6 - score_diffs_abs ** 4 / 180,
            )
    
    def cgf_derivative(self, score_diffs: NDArray) -> NDArray:
        with np.errstate(all='ignore'):
            return np.where(
                np.abs(score_diffs) < 1e-2,
                score_diffs / 3,
                1 / np.tanh(score_diffs) - 1 / score_diffs,
            )
    
    def cgf_2nd_derivative(self, score_diffs: NDArray) -> NDArray:
        with np.errstate(all='ignore'):
            return np.where(
                np.abs(score_diffs) < 1e-2,
                1 / 3 - score_diffs**2 / 15,
                1 / score_diffs**2 - 1 / np.tanh(score_diffs)**2 + 1,
            )


class Gaussian(RootLaw):
    def __init__(self, std: float):
        assert isinstance(std, (int, float)) and std > 0, std
        self.var = std**2

    def sup(self) -> float:
        return float("inf")
    
    def cgf(self, score_diffs: NDArray) -> NDArray:
        return score_diffs**2 * self.var / 2
        
    def cgf_derivative(self, score_diffs: NDArray) -> NDArray:
        return score_diffs * self.var
    
    def cgf_2nd_derivative(self, score_diffs: NDArray) -> NDArray:
        return np.ones(len(score_diffs)) * self.var


class Discrete(RootLaw):
    """ Discrete essentially corresponds to what is known as K-nary in 
    "Generalized Bradley-Terry Models for Score Estimation from Paired Comparisons" 
    by Julien Fageot, Sadegh Farhadkhani, Lê-Nguyên Hoang and Oscar Villemaud (AAAI'24).
    """
    def __init__(self, n_values: int):
        assert isinstance(n_values, int) and n_values >= 2, n_values
        self.n_values = n_values

    def normalize_rating(self, rating: Rating) -> float:
        middle = (rating.max + rating.min) / 2
        return float(2 * (rating.value - middle) / (rating.max - rating.min))
    
    def normalize_comparison(self, comparison: Comparison) -> float:
        return float(comparison.value / comparison.max)

    def sup(self) -> float:
        return 1.0
    
    def cgf(self, score_diffs: NDArray) -> NDArray:
        x, K = np.abs(score_diffs), self.n_values
        with np.errstate(all='ignore'):
            return np.where(
                x > 1e-1,
                np.where(
                    x < 20.0,
                    np.log( np.sinh(K * x / (K - 1)) / np.sinh(x / (K - 1)) ) - np.log(K),
                    x - np.log(K),
                ),
                x**2 * (K + 1) / (6 * (K - 1))
            )

    def cgf_derivative(self, score_diffs: NDArray) -> NDArray:
        x, K, Km1 = score_diffs, self.n_values, self.n_values - 1
        with np.errstate(all='ignore'):
            return np.where(
                np.abs(x) < 1e-2,
                x * (K + 1) / Km1 / 3,
                (K / np.tanh(K * x / Km1) - 1 / np.tanh(x / Km1)) / Km1
            )
    
    def cgf_2nd_derivative(self, score_diffs: NDArray) -> NDArray:
        x, K, Km1 = score_diffs, self.n_values, self.n_values - 1
        with np.errstate(all='ignore'):
            return (K + 1) / Km1 + np.where(
                np.abs(x) < 1e-2,
                (1 - K**4) * x**2 / (9 * Km1**4),
                (1.0 / np.tanh(x / Km1)**2 - K**2 / np.tanh(x * K / Km1)**2) / Km1**2
            )