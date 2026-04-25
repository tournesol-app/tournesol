from solidago import *
from solidago.recommenders import Chronological

poll = Poll(
    users = Users(["user_0", "user_1", "user_2"]),
    entities = Entities([
        ("entity_0", "user_0", 2), 
        ("entity_1", "user_0", 5), 
        ("entity_2", "user_1", 13), 
        ("entity_3", "user_2", 20),
        ("entity_4", "user_1", 25),
    ], columns=["name", "author", "date"]),
    socials = Socials([
        ("user_0", "user_1", "follow", 1.0, 0),
        ("user_0", "user_2", "follow", 1.2, 0),
        ("user_1", "user_0", "follow", 2.0, 0),
        ("user_1", "user_2", "follow", 1.5, 0),
        ("user_2", "user_0", "follow", 1.3, 0),
    ], columns=["to", "by", "kind", "weight", "priority"]),
    public_settings = PublicSettings(),
    ratings = Ratings([
        ("user_0", "entity_0", "repost", "atproto", 3),
        ("user_1", "entity_0", "repost", "atproto", 7),
        ("user_2", "entity_2", "repost", "atproto", 23),
        ("user_2", "entity_1", "repost", "atproto", 33),
    ], columns=["username", "entity_name", "criterion", "context", "timestamp"])
)

