from solidago import *
from solidago.primitives.instructions import Instructions

def test_init():
    assert Instructions(31531).value == 31531
    assert Instructions("oievwoi").value == "oievwoi"
    assert Instructions(3.14).value == 3.14
    assert Instructions(False).value == False
    assert Instructions(True).value == True
    assert Instructions(("hello", "world")).value == ["hello", "world"]
    assert Instructions({"hello": "world"}).value == {"hello": "world"}

def test_parse_range():
    assert Instructions._parse_range("range(5)") == [0, 1 ,2, 3, 4]
    assert Instructions._parse_range("range(2, 5)") == [2, 3, 4]
    assert Instructions._parse_range("range(2, 5, 2)") == [2, 4]
    assert Instructions._parse_range("range(2,5,2)") == [2, 4]

def test_parse_keys():
    assert Instructions.parse_keys("eqew.313.sdav.2t") == ["eqew", "313", "sdav", "2t"]
    assert Instructions.parse_keys("eqew") == ["eqew"]
    assert Instructions.parse_keys(313) == [313]
    
def test_load():
    instructions = Instructions.load("tests/generators/test_generator.yaml")
    assert instructions.has("modules")
    assert not instructions.has("module")
    assert instructions["modules.1"][0] == "entities.Entities"
    assert instructions["modules.1.n_entities"] == 8
    assert isinstance(instructions["modules.1"], list)
    assert len(instructions["modules.1"]) == 2
    instructions_clone = instructions.clone()
    instructions["items"] = dict(test=5)
    assert instructions["items.test"] == 5
    assert instructions.has("items")
    assert not instructions_clone.has("items")

def test_variables():
    variables = [
        ["aggregator source", "trim clip"],
        "attack.poison_ratio aggregator.n_poisons source",
        "model.input_size source"
    ]
    instructions = Instructions(dict(
        model=["LinearRegression", dict(input_size=[1, 4, 6])],
        attack=["AntiGradient", dict(poison_ratio=[1e-3, 1e-2])],
        aggregator=[
            ["Trim", dict(n_poisons=[1, 4, 6])],
            ["ClippedMean", dict(poison_ratio="&attack.poison_ratio")]
        ],
        source="{0}_{1}_{2}.pt"
    ))
    varnames, varname_values = instructions.parse_variables(variables)
    assert varnames == [["aggregator", "source"], ["attack.poison_ratio", "aggregator.n_poisons", "source"], ["model.input_size", "source"]]
    assert varname_values == [["trim", "clip"], [1e-3, 1e-2], [1, 4, 6]]

    extracted_instructions = instructions.extract_indices(varnames, varname_values, [1, 0, 2])
    assert instructions.value == dict(
        model=["LinearRegression", dict(input_size=[1, 4, 6])],
        attack=["AntiGradient", dict(poison_ratio=[1e-3, 1e-2])],
        aggregator=[
            ["Trim", dict(n_poisons=[1, 4, 6])],
            ["ClippedMean", dict(poison_ratio="&attack.poison_ratio")]
        ],
        source="{0}_{1}_{2}.pt"
    )

    assert extracted_instructions["attack.poison_ratio"] == 1e-3
    assert extracted_instructions["model.input_size"] == 6
    assert extracted_instructions["source"] == "clip_0.001_6.pt"
    assert extracted_instructions["aggregator.poison_ratio"] == 1e-3
    assert extracted_instructions.value == dict(
        model=["LinearRegression", dict(input_size=6)],
        attack=["AntiGradient", dict(poison_ratio=1e-3)],
        aggregator=["ClippedMean", dict(poison_ratio=1e-3)],
        source="clip_0.001_6.pt"
    )