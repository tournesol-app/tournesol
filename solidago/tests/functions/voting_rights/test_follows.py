from solidago import *

poll = Poll(
    users=Users(),
    entities=Entities(),
    socials=Socials(),
    public_settings=PublicSettings(),
    ratings=Ratings(),
    comparisons=Comparisons(),
    voting_rights=VotingRights(),
    user_models=UserModels(),
    global_model=ScoringModel(),
    past_recommendations=PastRecommendations(),
)