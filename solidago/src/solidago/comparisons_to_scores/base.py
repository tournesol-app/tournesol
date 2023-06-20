from abc import ABC, abstractmethod
from typing import Optional

import pandas as pd


class ComparisonsToScoresAlgorithm(ABC):
    @abstractmethod
    def compute_individual_scores(
        self, comparison_scores: pd.DataFrame, initial_entity_scores: Optional[pd.Series] = None
    ):
        """
        Computation of contributor scores and score uncertainties,
        based on their comparisons.

        At this stage, scores will not be normalized between contributors.

        Parameters
        ----------
        `comparison_scores`: pd.DataFrame, with columns:
            * `entity_a`: id of 1st compared entity
            * `entity_b`: id of 2nd compared entity
            * `score`: int, comparison score

        `initial_entity_scores`: pd.Series (optional) indexed by entity id.
            May help the algorithm to converge faster (for example).

        Returns
        -------
        pd.Dataframe, with index `entity_id`, and columns
            * `raw_score`: float, score of entity computed from the contributor comparions
            * `raw_uncertainty`: float, uncertainty on `raw_score`

        """
        ...

    @abstractmethod
    def get_metadata(self) -> dict:
        """
        Returns a dictionary with description of this algorithm instance.

        May be used for documentation purposes (e.g in Tournesol Public Dataset)
        """
        ...
