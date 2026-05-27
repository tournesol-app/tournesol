from solidago import *
from solidago.poll.scoring.model import DirectScores

poll = Poll(
    entities=Entities(['apple', 'banana', 'coconut', 'durian', 
        'etrog', 'fig', 'grape', 'hazelnut', 'imbe', 'jackfruit']),
    global_model=ScoringModel(directs=DirectScores([
        ("main", "apple", 10.),
        ("main", "banana", 1.),
        ("main", "coconut", 1.),
        ("main", "etrog", 1.),
        ("main", "fig", 1.),
        ("main", "grape", 0.1),
        ("main", "hazelnut", 1.),
        ("main", "imbe", 1.2),
        ("main", "jackfruit", -1.),
    ], columns=["criterion", "entity_name", "value"]))
)

def test_sampling_without_replacement():
    sampler = recommenders.sampler.SamplingWithoutReplacement()
    feeds = [sampler(poll, 5) for _ in range(100)]
    histogram = {e.name: 0 for e in poll.entities}
    for feed in feeds:
        for e in feed:
            histogram[e.name] = histogram[e.name] + 1
    assert all(len(f) == 5 for f in feeds)
    assert histogram["apple"] >= 90
    assert histogram["durian"] == histogram["jackfruit"] == 0
    assert histogram["grape"] < histogram["imbe"]