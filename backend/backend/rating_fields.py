"""List of ratings for a video."""

from collections import OrderedDict

# run the management command
# backend $ python manage.py js_constants --file ../frontend/src/constants.js
# to create the js version of constants

# Maximal value for a rating (0-100)
# 0 means left video is best, 100 means right video is best
MAX_VALUE = 100.

VIDEO_FIELDS_DICT = OrderedDict([
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

# Possible fields to report a video
VIDEO_REPORT_FIELDS = OrderedDict([
    ('troll', 'The content is a troll'),
    ('kid', 'The content is not kid-friendly'),
    ('misl0', 'The content is slightly misleading'),
    ('misl1', 'The content is very misleading'),
    ('misl2', 'The misinformation of the content is misleading and dangerous'),
    ('hate', 'The content contains hate speech'),
    ('violence', 'The content promotes violence'),
    ('bully', 'The content is cyber-bullying'),
    ('threat', 'The content contains threats'),
    ('violent_act', 'The content calls for violent acts'),
    ('death_threat', 'The content contains death threats'),
])

# maximal weight to assign to a rating for a particular feature, see #41
MAX_FEATURE_WEIGHT = 8
