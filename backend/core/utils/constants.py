"""
Define constants for Tournesol's main configuration
"""

featureIsEnabledByDeFault = {
    "largely_recommended": True,
    "reliability": False,
    "pedagogy": False,
    "importance": False,
    "engaging": False,
    "backfire_risk": False,
    "layman_friendly": False,
    "diversity_inclusion": False,
    "better_habits": False,
    "entertaining_relaxing": False,
}

# one symbol of a YouTube Video ID
YOUTUBE_VIDEO_ID_REGEX_SYMBOL = "[A-Za-z0-9-_]"

# The whole video ID
YOUTUBE_VIDEO_ID_REGEX = rf"^{YOUTUBE_VIDEO_ID_REGEX_SYMBOL}"+"{11}$"
