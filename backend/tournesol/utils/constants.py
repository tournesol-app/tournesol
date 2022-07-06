"""
Define constants for Tournesol's main configuration
"""

# one symbol of a YouTube Video ID
YOUTUBE_VIDEO_ID_REGEX_SYMBOL = "[A-Za-z0-9-_]"

# The whole video ID
YOUTUBE_VIDEO_ID_REGEX = rf"{YOUTUBE_VIDEO_ID_REGEX_SYMBOL}{{11}}"

# Maximal entity score after poll scaling is applied
MEHESTAN_MAX_SCALED_SCORE = 100.0

# Maximal absolute value for a comparison [-10, 10]
COMPARISON_MAX = 10.0
