"""List of ratings for a video."""

from collections import OrderedDict

# run the management command
# backend $ python manage.py js_constants --file ../frontend/src/constants.js
# to create the js version of constants

# Maximal value for a rating (0-100)
# 0 means left video is best, 100 means right video is best
MAX_VALUE = 100.

VIDEO_FIELDS_DICT = OrderedDict([
    ('largely_recommended', 'Should be largely recommended'),
    ('reliability', "Reliable and not misleading"),
    ('importance', "Important and actionable"),
    ('engaging', "Engaging and thought-provoking"),
    ('pedagogy', "Clear and pedagogical"),
    ('layman_friendly', "Layman-friendly"),
    ('diversity_inclusion', "Diversity and Inclusion"),
    ('backfire_risk', "Resilience to backfiring risks"),
    ('better_habits', 'Encourages better habits'),
    ('entertaining_relaxing', 'Entertaining and relaxing'),
])

VIDEO_FIELDS = list(VIDEO_FIELDS_DICT.keys())

# maximal weight to assign to a rating for a particular feature, see #41
MAX_FEATURE_WEIGHT = 8
