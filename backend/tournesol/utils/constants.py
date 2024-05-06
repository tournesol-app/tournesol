"""
Define constants for Tournesol's main configuration
"""

# one symbol of a YouTube Video ID
YOUTUBE_VIDEO_ID_REGEX_SYMBOL = "[A-Za-z0-9-_]"

# The whole video ID
YOUTUBE_VIDEO_ID_REGEX = rf"{YOUTUBE_VIDEO_ID_REGEX_SYMBOL}{{11}}"

# 3 seconds timeout to avoid staying blocked if an outgoing HTTP request fails
REQUEST_TIMEOUT = 3

# Maximal entity score after poll scaling is applied
MEHESTAN_MAX_SCALED_SCORE = 100.0

# Default weight for a criteria in the recommendations
# FIXME: the default weight used by the front end is 50, not 10
CRITERIA_DEFAULT_WEIGHT = 10
