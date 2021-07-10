from settings.settings import CRITERIAS_DICT, CRITERIAS, DRF_RECAPTCHA_PUBLIC_KEY

comments = {
    'featureNames': 'Dictionary mapping quality features to their description',
    'featureList': 'List of quality features in the correct order',
    'featureColors': 'Colors for quality features',
    'SEARCH_DIVIDER_COEFF': 'divide search score by this value',
    'SEARCH_FEATURE_CONST_ADD': 'add this value to Tournesol scores',
    'DRF_RECAPTCHA_PUBLIC_KEY': "Public ReCaptcha key",
    'featureIsEnabledByDeFault': "Is the feature enabled by-default?",
    'youtubeVideoIdRegexSymbol': "Regular expression of YouTube videos (one symbol)",
    'minNumRateLater': "Minimal number of videos to rate before redirecting to rating page",
    'DEFAULT_PREFS_VAL': "Default value of preferences for tournesol_score",
    'N_PUBLIC_CONTRIBUTORS_SHOW': 'Number of public contributors to show',
}

featureColors = {
    'largely_recommended': '#ff00ff',
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
    'largely_recommended': True,
    'reliability': False,
    'pedagogy': False,
    'importance': False,
    'engaging': False,
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

ts_constants = {
    'featureNames': CRITERIAS_DICT,
    'featureList': CRITERIAS,
    'featureColors': featureColors,
    'SEARCH_DIVIDER_COEFF': 100 * 20,
    'SEARCH_FEATURE_CONST_ADD': 0.,
    'DRF_RECAPTCHA_PUBLIC_KEY': DRF_RECAPTCHA_PUBLIC_KEY,
    'featureIsEnabledByDeFault': featureIsEnabledByDeFault,
    'youtubeVideoIdRegexSymbol': youtubeVideoIdRegexSymbol,
    'minNumRateLater': minNumRateLater,
    'DEFAULT_PREFS_VAL': 50.0,
    'N_PUBLIC_CONTRIBUTORS_SHOW': 10,
}
