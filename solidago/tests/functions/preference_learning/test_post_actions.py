from solidago import *
from solidago.poll.scoring.user_models import *

poll = Poll.load("tests/test_poll")


def test_post_actions_learning():
    from solidago.functions.preference_learning import PostActions
    learn = PostActions(dict(repost=1, report=-1), 10, max_workers=1)
    p = learn(poll)
    assert p.user_models["alice"](Entity("banana"), "post") == Score(1)
    assert p.user_models["alice"](Entity("etrog"), "post").isnan()
    assert p.user_models["alice"](Entity("etrog"), "repost") == Score(1)
    assert p.user_models["alice"](Entity("durian"), "repost").isnan()
    assert p.user_models["alice"](Entity("durian"), "report") == Score(-1)
    assert len(p.user_models["alice"].directs) == 7