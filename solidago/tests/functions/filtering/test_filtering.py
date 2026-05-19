from solidago import *

poll = Poll(
    Users([
        ("alice",   True), 
        ("bob",     False), 
        ("charlie", True), 
        ("dave",    True), 
        ("erin",    False),
    ], columns=["name", "pretrust"]),
    Entities([
        ("apple",   ("alice",),         (),             0), 
        ("banana",  ("alice", "bob"),   ("charlie",),   2), 
        ("coconut", ("alice",),         (),             21), 
        ("durian",  ("charlie",),       (),             26), 
        ("etrog",   ("dave", "erin"),   (),             54),
    ], columns=["name", "authors", "mentions", "date"]),
    Socials([
        ("alice",   "bob",      "vouch",    1.,     15),
        ("alice",   "bob",      "follow",   1.,     15),
        ("alice",   "charlie",  "follow",   1.,     30),
        ("alice",   "dave",     "follow",   1.,     31),
        ("alice",   "erin",     "vouch",    1.,     33),
        ("bob",     "alice",    "follow",   1.,     25),
        ("bob",     "dave",     "vouch",    1.,     32),
    ], colums=["by", "to", "kind", "weight", "date"]),
    PublicSettings([
        ("alice",   "coconut",  False),
        ("dave",    "durian",   False),
    ], columns=["username", "entity_name", "public"]),
    Ratings([
        
    ], columns=["username", "entity_name", "criterion", "context"]),
    Comparisons([
        
    ], columns=["username", "criterion", "context", "left_name", "right_name"]),
    VotingRights(),
    UserModels(),
    ScoringModel(),
    PastRecommendations(),
)