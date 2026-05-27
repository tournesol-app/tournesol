from solidago import *
poll = Poll.load("tests/test_poll")

def test_chronofair():
    rec = recommenders.ChronoFair()
    rec.customize("alice", 100)
    p = rec.preprocess(poll)
    scores = p.global_model(criterion="main")
    feeds = [recommenders.ChronoFair()(poll, 5, "alice", None, 100) for _ in range(100)]
    histogram = {e.name: 0 for e in poll.entities}
    for feed in feeds:
        for e in feed:
            histogram[e.name] = histogram[e.name] + 1
    assert all(
        histogram[e.name] == 0 for e in poll.entities 
        if e.name not in scores("entity_name") or scores.get(entity_name=e.name)["value"] <= 0
    )