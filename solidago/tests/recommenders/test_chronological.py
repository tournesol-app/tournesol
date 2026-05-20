from solidago import *
from solidago.primitives.datastructure.named_objects import Contains
from solidago.recommenders import Chronological

poll = Poll(
    users = Users(["user_0", "user_1", "user_2", "user_3"]),
    entities = Entities([
        ("entity_0", ("user_0",), 2), 
        ("entity_1", ("user_0",), 5), 
        ("entity_2", ("user_1",), 13), 
        ("entity_3", ("user_2",), 20),
        ("entity_4", ("user_1",), 25),
        ("entity_5", ("user_3",), 30),
    ], columns=["name", "authors", "timestamp"]),
    socials = Socials([
        ("user_0", "user_1", "follow", 1.0),
        ("user_0", "user_2", "follow", 1.2),
        ("user_1", "user_0", "follow", 2.0),
        ("user_1", "user_2", "follow", 1.5),
        ("user_2", "user_0", "follow", 1.3),
    ], columns=["to", "by", "kind", "weight"]),
    public_settings = PublicSettings(),
    ratings = Ratings([
        ("user_0", "entity_0", "repost", "atproto", 3),
        ("user_1", "entity_0", "repost", "atproto", 7),
        ("user_2", "entity_2", "repost", "atproto", 23),
        ("user_2", "entity_1", "repost", "atproto", 33),
        ("user_2", "entity_5", "repost", "atproto", 37),
    ], columns=["username", "entity_name", "criterion", "context", "timestamp"])
)


def test_detailed_chronological():
    follow_kind, rating_criteria = "follow", ["repost"]
    receiver_name, limit, cursor = "user_0", 4, None

    followings = poll.socials.filters(by=receiver_name, kind=follow_kind)("to")
    reposts = poll.ratings.filters(username=followings, criterion=rating_criteria)
    names = set(poll.entities.filters(authors=Contains(followings)).names())
    entities = poll.entities.filters(names | reposts.keys("entity_name"))
    entities = entities.assign(last_timestamp=entities("timestamp"))
    
    if receiver_name is not None:
        entities = entities.excludes(authors=Contains(receiver_name))

    for repost in reposts:
            name = repost["entity_name"]
            if receiver_name not in poll.entities[name]["authors"]:
                timestamp = repost.get("timestamp", 0)
                last_timestamp = entities[name].get("last_timestamp", -1)
                last_timestamp = max(timestamp, last_timestamp)
                entities[name, "last_timestamp"] = last_timestamp
        
    try:
        offset = 0 if cursor is None else int(cursor)
    except ValueError:
        offset = 0
    
    entities = entities.sort_by("last_timestamp", ascending=False)
    entities = entities.tail(len(entities) - offset).head(limit)
    
    assert list(entities.names()) == ["entity_5", "entity_4", "entity_2", "entity_3"]
    
    
def test_chronological():    
    entities = Chronological()(poll, 2, "user_0", "0")
    assert list(entities.names()) == ["entity_5", "entity_4"]
    entities = Chronological()(poll, 3, "user_0", "1")
    assert list(entities.names()) == ["entity_4", "entity_2", "entity_3"]
    