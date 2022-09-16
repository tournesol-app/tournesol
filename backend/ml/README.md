Tournesol ML algorithms
===

This application contains the implementation of the algorithms responsible for computing individual
and collective scores for entities (videos, etc), based on the comparisons submitted by Tournesol users.


# Algorithm

The current implementation is derived from **Mehestan**, a novel mechanism for _Robust Sparse Voting_ described in [arXiv:2202.08656](https://doi.org/10.48550/arXiv.2202.08656).

A complete theoretical framework, adapted specifically for Tournesol, is to be published soon...


# Organisation

* `management/commands/` contains `ml_train`, the Django management command used to run the actual job computing the scores.

* `inputs.py`: generic input structures for Tournesol algorithms, implementing 2 methods:
    * `get_comparisons()` to fetch a comparisons database
    * `get_rating_properties()` to fetch rating properties related to each pair (user, entity), visibility, trust status, etc.

* `outputs.py`: generic methods to save computed scores and scalings into the Tournesol database

* `mehestan/` contains the implementation of the mechanisms specific to Mehestan:
  * primitives.py: fundamental functions for Mehestan, including `QrMed` (the Quadratically Regularized Median), and `BrMean` (the Byzantine-Robustified Mean)
  * individual.py: computation of individual scores, derived from comparison scores submitted by each user
  * global_scores.py: computation of scaling parameters and aggregated scores, based on the individual scores associated to each entity
  * run.py: glue code to integrate Mehestan with ml inputs/outputs and implement parallelization strategies
