from abc import abstractmethod
from typing import Any, Union
from numpy.typing import NDArray
from numba import njit

import numpy as np

from solidago.poll import *


class RootLaw:
    def __init__(self, *args, **kwargs):
        pass

    def normalize_rating(self, rating: Rating) -> float:
        return float(rating["value"])
    
    def normalize_comparison(self, comparison: Comparison) -> float:
        return float(comparison["value"])
    
    def get_arg(self) -> int | float | None:
        return None

    @abstractmethod
    def sup(self, *args: Any) -> float:
        """ Supremum on the set of allowed value_diff. Also equals sup of cgf_derivative, see Theorem 1 of
        "Generalized Bradley-Terry Models for Score Estimation from Paired Comparisons" 
        by Julien Fageot, Sadegh Farhadkhani, Lê-Nguyên Hoang and Oscar Villemaud (AAAI'24). """

    def inf(self, *args: Any) -> float:
        return - self.sup(*args)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({', '.join([f'{k}={v}' for k, v in self.__dict__.items()])})"


class BradleyTerry(RootLaw):
    def normalize_rating(self, rating: Rating) -> float:
        mean = (rating["min"] + rating["max"]) / 2
        mean = 0 if np.isfinite(mean) else mean
        return np.sign(rating["value"] - mean)
    
    def normalize_comparison(self, comparison: Comparison) -> float:
        return np.sign(comparison["value"])
    
    def sup(self, *args: Any) -> float:
        return 1.0

    @staticmethod
    @njit
    def cgf(score_diffs: NDArray[np.float64]) -> NDArray[np.float64]:
        """ The cgf of UniformGBT is simply log( cosh(value_diff) ).
        However, numerical accuracy requires care when abs(value_diff) is large.
        """
        score_diffs_abs = np.abs(score_diffs)
        return np.where(
            score_diffs_abs < 20.0,
            np.log(np.cosh(score_diffs)),
            score_diffs_abs - np.log(2),
        )
        
    @staticmethod
    @njit
    def cgf1(score_diffs: NDArray[np.float64]) -> NDArray[np.float64]:
        return np.tanh(score_diffs)
        
    @staticmethod
    @njit
    def cgf2(score_diffs: NDArray[np.float64]) -> NDArray[np.float64]:
        return 1 / np.cosh(score_diffs)**2


class Uniform(RootLaw):
    def normalize_rating(self, rating: Rating) -> float:
        middle = (rating["max"] + rating["min"]) / 2
        return float(2 * (rating["value"] - middle) / (rating["max"] - rating["min"]))
    
    def normalize_comparison(self, comparison: Comparison) -> float:
        return float(comparison["value"] / comparison["max"])
    
    def sup(self, *args: Any) -> float:
        return 1.0
    
    @staticmethod
    @njit
    def cgf(score_diffs: NDArray[np.float64]) -> NDArray[np.float64]:
        """ The cgf of UniformGBT is simply log( sinh(value_diff) / value_diff ).
        However, numerical accuracy requires care when abs(value_diff) is small 
        (because of division by zero) or large (because sinh explodes).
        We use series expansion approximation for these cases.
        """
        score_diffs_abs = np.abs(score_diffs)
        return np.where(
            score_diffs_abs > 1e-1,
            np.where(
                score_diffs_abs < 20.0,
                np.log(np.sinh(score_diffs) / score_diffs),
                score_diffs_abs - np.log(2) - np.log(score_diffs_abs),
            ),
            score_diffs_abs ** 2 / 6 - score_diffs_abs ** 4 / 180,
        )
        
    @staticmethod
    @njit
    def cgf1(score_diffs: NDArray[np.float64]) -> NDArray[np.float64]:
        return np.where(
            np.abs(score_diffs) < 1e-2,
            score_diffs / 3,
            1 / np.tanh(score_diffs) - 1 / score_diffs,
        )
        
    @staticmethod
    @njit
    def cgf2(score_diffs: NDArray[np.float64]) -> NDArray[np.float64]:
        return np.where(
            np.abs(score_diffs) < 1e-2,
            1 / 3 - score_diffs**2 / 15,
            1 / score_diffs**2 - 1 / np.tanh(score_diffs)**2 + 1,
        )


class Gaussian(RootLaw):
    def __init__(self, std: float):
        assert isinstance(std, (int, float))
        self.std = std
    
    def get_arg(self) -> int | float | None:
        return self.std

    def sup(self, *args) -> float:
        return float("inf")
    
    @staticmethod
    @njit
    def cgf(score_diffs: NDArray[np.float64], arg: NDArray[np.float64]) -> NDArray[np.float64]: # arg == std
        return score_diffs**2 / (2 * arg**2)
    
    @staticmethod
    @njit
    def cgf1(score_diffs: NDArray[np.float64], arg: NDArray[np.float64]) -> NDArray[np.float64]: # arg == std
        return score_diffs / arg**2
    
    @staticmethod
    @njit
    def cgf2(score_diffs: NDArray[np.float64], arg: NDArray[np.float64]) -> NDArray[np.float64]: # arg == std
        return np.ones(len(score_diffs)) / arg**2


class Discrete(RootLaw):
    """ Discrete essentially corresponds to what is known as K-nary in 
    "Generalized Bradley-Terry Models for Score Estimation from Paired Comparisons" 
    by Julien Fageot, Sadegh Farhadkhani, Lê-Nguyên Hoang and Oscar Villemaud (AAAI'24).
    """
    def __init__(self, n_values: int):
        assert n_values >= 2, n_values
        self.n_values = int(n_values)
    
    def get_arg(self) -> int | float | None:
        return self.n_values

    def normalize_rating(self, rating: Rating) -> float:
        middle = (rating["max"] + rating["min"]) / 2
        return float(2 * (rating["value"] - middle) / (rating["max"] - rating["min"]))
    
    def normalize_comparison(self, comparison: Comparison) -> float:
        if np.isfinite(comparison["max"]):
            return float(comparison["value"] / comparison["max"])
        return float(comparison["value"])

    def sup(self, *args: Any) -> float:
        return 1.0
    
    @staticmethod
    @njit
    def cgf(score_diffs: NDArray[np.float64], arg: NDArray[np.int64]) -> NDArray[np.float64]: # arg == n_values
        x, K, Km1 = np.abs(score_diffs), arg, arg - 1
        return np.where(
            x > 1e-1,
            np.where(
                x < 20.0,
                np.log( np.sinh(K * x / Km1) / np.sinh(x / Km1) ) - np.log(K),
                x - np.log(K),
            ),
            x**2 * (K + 1) / (6 * Km1)
        )
        
    @staticmethod
    @njit
    def cgf1(score_diffs: NDArray[np.float64], arg: NDArray[np.int64]) -> NDArray[np.float64]: # arg == n_values
        x, K, Km1 = score_diffs, arg, arg - 1
        return np.where(
            np.abs(x) < 1e-2,
            x * (K + 1) / Km1 / 3,
            (K / np.tanh(K * x / Km1) - 1 / np.tanh(x / Km1)) / Km1
        )
        
    @staticmethod
    @njit
    def cgf2(score_diffs: NDArray[np.float64], arg: NDArray[np.int64]) -> NDArray[np.float64]: # arg == n_values
        x, K, Km1 = np.abs(score_diffs), arg, arg - 1
        return (K + 1) / Km1 + np.where(
            np.abs(x) < 1e-2,
            (1 - K**4) * x**2 / (9 * Km1**4),
            (1.0 / np.tanh(x / Km1)**2 - K**2 / np.tanh(x * K / Km1)**2) / Km1**2
        )