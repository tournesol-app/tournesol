import random

import pandas as pd
import pytest

from ml.mehestan.individual import compute_individual_score
from ml.mehestan.individual_bbt import compute_individual_score as compute_individual_score_bbt


@pytest.mark.parametrize(
    "compute_method", [compute_individual_score, compute_individual_score_bbt]
)
class TestIndividualScores:
    def test_all_comparisons_zero(self, compute_method):
        comparisons = pd.DataFrame(
            [
                {
                    "entity_a": "video_1",
                    "entity_b": "video_2",
                    "score": 0,
                },
                {
                    "entity_a": "video_2",
                    "entity_b": "video_3",
                    "score": 0,
                },
            ]
        )
        scores = compute_method(comparisons)
        for video in ["video_1", "video_2", "video_3"]:
            assert scores.loc[video].raw_score == 0
            assert scores.loc[video].raw_uncertainty > 0

    def test_comparisons_chain(self, compute_method):
        comparisons = pd.DataFrame(
            [
                {
                    "entity_a": f"video_{idx:02d}",
                    "entity_b": f"video_{idx+1:02d}",
                    "score": 10,
                }
                for idx in range(20)
            ]
        )
        scores = compute_method(comparisons)
        scores.sort_values("raw_score", inplace=True)

        # Video are ranked according to the chain of comparisons
        assert list(scores.index) == sorted(scores.index)

        # Compared videos are indexed 0 to 20 included; video_10 is in the middle with score 0.0
        assert scores.loc["video_10"].raw_score == pytest.approx(0.0, abs=1e-4)
        for idx in range(10):
            assert scores.iloc[idx].raw_score == pytest.approx(-1 * scores.iloc[20-idx].raw_score, abs=1e-4)

    def test_individual_scores_mean_is_zero(self, compute_method):
        comparisons = [
            ("A", "B", random.randint(-10, 10)),
            ("A", "C", random.randint(-10, 10)),
            ("A", "D", random.randint(-10, 10)),
            ("B", "C", random.randint(-10, 10)),
            ("B", "D", random.randint(-10, 10)),
            ("C", "D", random.randint(-10, 10)),
        ]
        comparisons_df = pd.DataFrame(comparisons, columns=["entity_a", "entity_b", "score"])
        scores = compute_method(comparisons_df)
        assert scores.raw_score.mean() == pytest.approx(0.0, abs=1e-4)

    def test_comparisons_strong_preferences(self, compute_method):
        if compute_method is compute_individual_score:
            pytest.xfail("The non-BBT version does not preserve preferences order :( ")

        comparisons = [
            ("A", "B", 0),
            ("A", "C", 0),
            ("A", "D", 0),
            ("B", "C", 0),
            ("B", "D", 0),
            ("C", "D", 0),
            # strong preferences
            ("A", "E", 9),
            ("B", "F", 10),
        ]
        comparisons_df = pd.DataFrame(comparisons, columns=["entity_a", "entity_b", "score"])
        scores = compute_method(comparisons_df)

        # F is preferred to E
        assert scores.loc["F"].raw_score > scores.loc["E"].raw_score

    def test_comparisons_monotony(self, compute_method):
        if compute_method is compute_individual_score:
            pytest.xfail("The non-BBT version does not preserve monotony")

        comparisons_1 = [
            ("A", "B", 8),
            ("A", "C", 9),
            ("A", "D", 10),
            ("B", "C", 8),
            ("B", "D", 9),
            ("C", "D", 10),
        ]

        # Move preferences towards A
        comparisons_2 = [
            ("A", "B", 7),
            ("A", "C", 8),
            ("A", "D", 9),
            ("B", "C", 8),
            ("B", "D", 9),
            ("C", "D", 10),
        ]

        comparisons_1_df = pd.DataFrame(comparisons_1, columns=["entity_a", "entity_b", "score"])
        scores_1 = compute_method(comparisons_1_df)
        comparisons_2_df = pd.DataFrame(comparisons_2, columns=["entity_a", "entity_b", "score"])
        scores_2 = compute_method(comparisons_2_df)

        assert scores_2.loc["A"].raw_score > scores_1.loc["A"].raw_score

    def test_comparisons_non_connex(self, compute_method):
        comparisons = [
            # Group 1
            ("A", "B", -1),
            ("A", "C", 0),
            ("A", "D", 1),
            # Group 2
            ("E", "F", -1),
            ("E", "G", 0),
            ("E", "H", 1),
        ]
        comparisons_df = pd.DataFrame(comparisons, columns=["entity_a", "entity_b", "score"])
        scores = compute_method(comparisons_df)

        assert scores.loc["A"].raw_score == pytest.approx(0.0, abs=1e-4)
        assert scores.loc["A"].raw_score == pytest.approx(scores.loc["E"].raw_score, abs=1e-4)
        assert scores.loc["B"].raw_score == pytest.approx(scores.loc["F"].raw_score, abs=1e-4)
        assert scores.loc["C"].raw_score == pytest.approx(scores.loc["G"].raw_score, abs=1e-4)
        assert scores.loc["D"].raw_score == pytest.approx(scores.loc["H"].raw_score, abs=1e-4)
