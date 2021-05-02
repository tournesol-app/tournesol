// Tournesol constants file
// Auto-generated file by generate_js_code python function
// To re-create, run backend $ python manage.py js_constants --file ../frontend/src/constants.js

// Dictionary mapping quality features to their description
export const featureNames = JSON.parse(`{
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

// Dictionary mapping video report fields to their descriptions
export const videoReportFieldNames = JSON.parse(`{
    "troll": "The content is a troll",
    "kid": "The content is not kid-friendly",
    "misl0": "The content is slightly misleading",
    "misl1": "The content is very misleading",
    "misl2": "The misinformation of the content is misleading and dangerous",
    "hate": "The content contains hate speech",
    "violence": "The content promotes violence",
    "bully": "The content is cyber-bullying",
    "threat": "The content contains threats",
    "violent_act": "The content calls for violent acts",
    "death_threat": "The content contains death threats"
}`);

// divide search score by this value
export const SEARCH_DIVIDER_COEFF = JSON.parse('2000');

// add this value to Tournesol scores
export const SEARCH_FEATURE_CONST_ADD = JSON.parse('0.0');

// List of video report fields
export const videoReportFields = JSON.parse(`[
    "troll",
    "kid",
    "misl0",
    "misl1",
    "misl2",
    "hate",
    "violence",
    "bully",
    "threat",
    "violent_act",
    "death_threat"
]`);

// Public ReCaptcha key
export const DRF_RECAPTCHA_PUBLIC_KEY = JSON.parse('"get_yours_from_recaptcha"');

// Is the feature enabled by-default?
export const featureIsEnabledByDeFault = JSON.parse(`{
    "reliability": true,
    "pedagogy": false,
    "importance": true,
    "engaging": true,
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
