from backend.rating_fields import VIDEO_FIELDS_DICT, VIDEO_FIELDS, VIDEO_REPORT_FIELDS
from django_react.settings import DRF_RECAPTCHA_PUBLIC_KEY

comments = {
    'featureNames': 'Dictionary mapping quality features to their description',
    'featureList': 'List of quality features in the correct order',
    'featureColors': 'Colors for quality features',
    'videoReportFieldNames':
        'Dictionary mapping video report fields to their descriptions',
    'SEARCH_DIVIDER_COEFF': 'divide search score by this value',
    'SEARCH_FEATURE_CONST_ADD': 'add this value to Tournesol scores',
    'videoReportFields': 'List of video report fields',
    'DRF_RECAPTCHA_PUBLIC_KEY': "Public ReCaptcha key",
    'featureIsEnabledByDeFault': "Is the feature enabled by-default?",
    'youtubeVideoIdRegexSymbol': "Regular expression of YouTube videos (one symbol)",
    'minNumRateLater': "Minimal number of videos to rate before redirecting to rating page",
}

featureColors = {
    'reliability': '#6573c3',
    'pedagogy': '#8561c5',
    'importance': '#ff784e',
    'engaging': '#ffc107',
    'backfire_risk': '#e91e63',
    'layman_friendly': '#50f22c',
    'diversity_inclusion': '#2ceff2',
    'better_habits': '#c6eb34',
    'entertaining_relaxing': '#6ba4ff',
}

featureIsEnabledByDeFault = {
    'reliability': True,
    'pedagogy': False,
    'importance': True,
    'engaging': True,
    'backfire_risk': False,
    'layman_friendly': False,
    'diversity_inclusion': False,
    'better_habits': False,
    'entertaining_relaxing': False,
}

# one symbol of a YouTube Video ID
youtubeVideoIdRegexSymbol = '[A-Za-z0-9-_]'

# The whole video ID
youtubeVideoIdRegex = rf'^{youtubeVideoIdRegexSymbol}+$'

# minimal number of videos to add to redirect to rating, see #281
minNumRateLater = 6

# number of top popular videos
n_top_popular = 100

fields = {
    'featureNames': VIDEO_FIELDS_DICT,
    'featureList': VIDEO_FIELDS,
    'featureColors': featureColors,
    'videoReportFieldNames': VIDEO_REPORT_FIELDS,
    'SEARCH_DIVIDER_COEFF': 100 * 20,
    'SEARCH_FEATURE_CONST_ADD': 0.,
    'videoReportFields': list(
        VIDEO_REPORT_FIELDS.keys()),
    'DRF_RECAPTCHA_PUBLIC_KEY': DRF_RECAPTCHA_PUBLIC_KEY,
    'featureIsEnabledByDeFault': featureIsEnabledByDeFault,
    'youtubeVideoIdRegexSymbol': youtubeVideoIdRegexSymbol,
    'minNumRateLater': minNumRateLater,
}
