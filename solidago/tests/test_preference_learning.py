import importlib
import random

import numpy as np
import pandas as pd
import pytest

import solidago.preference_learning as preference_learning


@pytest.mark.parametrize("test", range(4))
def test_uniform_gbt(test):
    td = importlib.import_module(f"data.data_{test}")
    models = td.pipeline.preference_learning(td.judgments, td.users, td.entities)
    for user in td.users.index:
        for entity in td.entities.index:
            output = models[user](entity)
            target = td.learned_models[user](entity, td.entities.loc[entity])
            assert output == pytest.approx(target, abs=1e-1), (user, entity)


@pytest.mark.parametrize("test", range(4))
def test_lbfgs_uniform_gbt(test):
    pytest.importorskip("torch")
    LBFGSUniformGBT = preference_learning.LBFGSUniformGBT
    td = importlib.import_module(f"data.data_{test}")
    models = LBFGSUniformGBT()(td.judgments, td.users, td.entities)
    for user in td.users.index:
        for entity in td.entities.index:
            output = models[user](entity)
            target = td.learned_models[user](entity, td.entities.loc[entity])
            assert output == pytest.approx(target, abs=1e-1), (user, entity)


@pytest.mark.parametrize("method", ["UniformGBT", "LBFGSUniformGBT"])
class TestGBT:
    @pytest.fixture
    def gbt(self, method):
        if method == "LBFGSUniformGBT":
            pytest.importorskip("torch")
        yield getattr(preference_learning, method)()

    def test_gbt_score_zero(self, gbt):
        model = gbt.comparison_learning(
            comparisons=pd.DataFrame(
                {
                    "entity_a": [1, 1],
                    "entity_b": [2, 3],
                    "comparison": [0, 0],
                    "comparison_max": [10, 10],
                }
            )
        )

        assert model(entity_id=1) == pytest.approx((0, 1.8, 1.8), abs=0.1)
        assert model(entity_id=2) == pytest.approx((0, 2.7, 2.7), abs=0.1)
        assert model(entity_id=3) == pytest.approx((0, 2.7, 2.7), abs=0.1)

    def test_comparisons_chain(self, gbt):
        comparisons = pd.DataFrame(
            [
                {
                    "entity_a": f"video_{idx:02d}",
                    "entity_b": f"video_{idx+1:02d}",
                    "comparison": 10,
                    "comparison_max": 10,
                }
                for idx in range(20)
            ]
        )
        model = gbt.comparison_learning(comparisons=comparisons)
        scores = {
            entity_id: score for (entity_id, (score, _left, _right)) in model.iter_entities()
        }

        # Video are ranked according to the chain of comparisons
        assert sorted(scores.keys()) == sorted(scores.keys(), key=lambda e: scores[e])

        # Compared videos are indexed 0 to 20 included; video_10 is in the middle with score 0.0
        assert scores["video_10"] == pytest.approx(0.0, abs=1e-1)
        for idx in range(10):
            assert scores[f"video_{idx:02d}"] == pytest.approx(
                -1 * scores[f"video_{(20 - idx):02d}"], abs=1e-1
            )

    def test_individual_scores_mean_is_zero(self, gbt):
        comparisons = [
            ("A", "B", random.randint(-10, 10)),
            ("A", "C", random.randint(-10, 10)),
            ("A", "D", random.randint(-10, 10)),
            ("B", "C", random.randint(-10, 10)),
            ("B", "D", random.randint(-10, 10)),
            ("C", "D", random.randint(-10, 10)),
        ]
        comparisons_df = pd.DataFrame(comparisons, columns=["entity_a", "entity_b", "comparison"])
        comparisons_df["comparison_max"] = 10
        model = gbt.comparison_learning(comparisons=comparisons_df)
        scores = [score for (_, (score, _, _)) in model.iter_entities()]
        assert np.mean(scores) == pytest.approx(0.0, abs=1e-1)

    def test_comparisons_strong_preferences(self, gbt):
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
        comparisons_df = pd.DataFrame(comparisons, columns=["entity_a", "entity_b", "comparison"])
        comparisons_df["comparison_max"] = 10
        model = gbt.comparison_learning(comparisons=comparisons_df)

        # F is preferred to E
        E_score = model["E"][0]
        F_score = model["F"][0]
        assert F_score > E_score

    def test_comparisons_monotony(self, gbt):
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

        comparisons_1_df = pd.DataFrame(
            comparisons_1, columns=["entity_a", "entity_b", "comparison"]
        ).assign(comparison_max=10)

        model_1 = gbt.comparison_learning(comparisons=comparisons_1_df)
        comparisons_2_df = pd.DataFrame(
            comparisons_2, columns=["entity_a", "entity_b", "comparison"]
        ).assign(comparison_max=10)
        model_2 = gbt.comparison_learning(comparisons=comparisons_2_df)

        A_score_model_1 = model_1["A"][0]
        A_score_model_2 = model_2["A"][0]
        assert A_score_model_2 > A_score_model_1

    def test_comparisons_non_connex(self, gbt):
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
        comparisons_df = pd.DataFrame(comparisons, columns=["entity_a", "entity_b", "comparison"])
        comparisons_df["comparison_max"] = 10
        model = gbt.comparison_learning(comparisons=comparisons_df)
        scores = {
            entity_id: score for (entity_id, (score, _left, _right)) in model.iter_entities()
        }

        assert scores["A"] == pytest.approx(0.0, abs=1e-2)
        assert scores["A"] == pytest.approx(scores["E"], abs=1e-2)
        assert scores["B"] == pytest.approx(scores["F"], abs=1e-2)
        assert scores["C"] == pytest.approx(scores["G"], abs=1e-2)
        assert scores["D"] == pytest.approx(scores["H"], abs=1e-2)
