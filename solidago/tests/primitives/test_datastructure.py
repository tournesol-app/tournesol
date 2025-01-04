import pytest
from solidago.primitives.datastructure import *

from pandas import DataFrame


jobs = NestedDictOfItems(
    d=DataFrame([
        ["supermarket", "cashier", "ok"], 
        ["supermarket", "logistic", "cool"], 
        ["bank", "programmer", "no, thanks!"],
    ], columns=["company", "job", "appreciation"]),
    key_names=["company", "job"], 
    value_name="appreciation",
    default_value="unknown"
)

animals = NestedDictOfTuples(
    d={ "elephant": { "water": (True, 5) }, "dog": { "meat": (False, 3) } },
    key_names=["animal", "food"], 
    value_names=["essential_need", "quantity"],
)
animals = NestedDictOfTuples(
    animals,
    key_names=["animal", "food"], 
    value_names=["essential_need", "quantity"],
)

population = NestedDictOfRowLists(
    d={ "young": { "rich": [{ "quality": "dynamic" }], "poor": [{"quality": "modest", "fun": True }] } },
    key_names=["age", "welfare"]
)

@pytest.mark.parametrize("d,expected_result", [
    (jobs, "unknown"), 
    (animals, None), 
    (population, list())
])
def test_default_value(d, expected_result):
    assert d["paris", "france"] == expected_result
