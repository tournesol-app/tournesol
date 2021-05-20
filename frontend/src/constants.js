// Tournesol constants file
// Auto-generated file by generate_js_code python function
// To re-create, run backend $ python manage.py js_constants --file ../frontend/src/constants.js

// Dictionary mapping quality features to their description
export const featureNames = JSON.parse(`{
    "largely_recommended": "Should be largely recommended",
    "reliability": "Reliable and not misleading",
    "importance": "Important and actionable",
    "engaging": "Engaging and thought-provoking",
    "pedagogy": "Clear and pedagogical",
    "layman_friendly": "Layman-friendly",
    "diversity_inclusion": "Diversity and Inclusion",
    "backfire_risk": "Resilience to backfiring risks",
    "better_habits": "Encourages better habits",
    "entertaining_relaxing": "Entertaining and relaxing"
}`);

// List of quality features in the correct order
export const featureList = JSON.parse(`[
    "largely_recommended",
    "reliability",
    "importance",
    "engaging",
    "pedagogy",
    "layman_friendly",
    "diversity_inclusion",
    "backfire_risk",
    "better_habits",
    "entertaining_relaxing"
]`);

// Colors for quality features
export const featureColors = JSON.parse(`{
    "largely_recommended": "#ff00ff",
    "reliability": "#6573c3",
    "pedagogy": "#8561c5",
    "importance": "#ff784e",
    "engaging": "#ffc107",
    "backfire_risk": "#e91e63",
    "layman_friendly": "#50f22c",
    "diversity_inclusion": "#2ceff2",
    "better_habits": "#c6eb34",
    "entertaining_relaxing": "#6ba4ff"
}`);

// divide search score by this value
export const SEARCH_DIVIDER_COEFF = JSON.parse('2000');

// add this value to Tournesol scores
export const SEARCH_FEATURE_CONST_ADD = JSON.parse('0.0');

// Public ReCaptcha key
export const DRF_RECAPTCHA_PUBLIC_KEY = JSON.parse('"get_yours_from_recaptcha"');

// Is the feature enabled by-default?
export const featureIsEnabledByDeFault = JSON.parse(`{
    "largely_recommended": true,
    "reliability": false,
    "pedagogy": false,
    "importance": false,
    "engaging": false,
    "backfire_risk": false,
    "layman_friendly": false,
    "diversity_inclusion": false,
    "better_habits": false,
    "entertaining_relaxing": false
}`);

// Regular expression of YouTube videos (one symbol)
export const youtubeVideoIdRegexSymbol = JSON.parse('"[A-Za-z0-9-_]"');

// Minimal number of videos to rate before redirecting to rating page
export const minNumRateLater = JSON.parse('6');

// Default value of preferences for tournesol_score
export const DEFAULT_PREFS_VAL = JSON.parse('50.0');

// Number of public contributors to show
export const N_PUBLIC_CONTRIBUTORS_SHOW = JSON.parse('10');
