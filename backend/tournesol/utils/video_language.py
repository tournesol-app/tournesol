import re
from collections import Counter

from django.conf import settings
from langdetect import DetectorFactory, detect, lang_detect_exception

LANGUAGE_CODE_TO_NAME_MATCHING = dict(settings.LANGUAGES)
ACCEPTED_LANGUAGE_CODES = set(LANGUAGE_CODE_TO_NAME_MATCHING.keys())

# Language configurations supported by Postgres full-text search
POSTGRES_LANGUAGES = (
    "arabic",
    "danish",
    "dutch",
    "english",
    "finnish",
    "french",
    "german",
    "greek",
    "hungarian",
    "indonesian",
    "irish",
    "italian",
    "lithuanian",
    "nepali",
    "norwegian",
    "portuguese",
    "romanian",
    "russian",
    "spanish",
    "swedish",
    "tamil",
    "turkish",
)

# Personalized configurations, notably used for automatically removing accents
POSTGRES_SEARCH_CONFIGS = ["customized_" + language for language in POSTGRES_LANGUAGES]
SEARCH_CONFIG_CHOICES = list(zip(POSTGRES_SEARCH_CONFIGS, POSTGRES_LANGUAGES))

# Add the "generic" default configuration for languages not supported by Postgres.
DEFAULT_SEARCH_CONFIG = "generic"
POSTGRES_SEARCH_CONFIGS.append(DEFAULT_SEARCH_CONFIG)
SEARCH_CONFIG_CHOICES.append((DEFAULT_SEARCH_CONFIG, "other language config"))

# Enforce consistent results with a constant seed,
# as the language detection algorithm is non-deterministic.
# See https://github.com/Mimino666/langdetect#basic-usage
DetectorFactory.seed = 0


def languages_detection(title, description):
    ''' This algo make 18 errors / 1238 known video (1.45 % of error) '''

    # Remove lines which contains links, mail or year
    description = [line for line in description.split('\n')
                   if not re.search(r'^(17|18|19|20)\d{2}|www|http|@$', line)]
    text = title + ' '.join(description)
    text = re.sub(r'\W+', ' ', text)
    text = text.lower()

    try:
        lang = detect(text)
    except lang_detect_exception.LangDetectException:
        lang = None

    return lang


def compute_video_language(uploader, title, description):
    from tournesol.models.entity import Entity  # pylint: disable=import-outside-toplevel

    # Get language(s) from other videos of the same uploader
    lang_list = (
        Entity.objects
        .filter(metadata__uploader=uploader)
        .values_list("metadata__language")
    )

    if lang_list:
        main_uploader_lang, main_uploader_lang_cnt = Counter(lang_list).most_common()[0]
        if len(lang_list) > 4 and main_uploader_lang_cnt/len(lang_list) > 0.9:
            return main_uploader_lang[0]

    lang = languages_detection(title, description)
    if lang in ACCEPTED_LANGUAGE_CODES:
        return lang
    return None


def language_to_postgres_config(language_code):
    """
    Used to convert language codes in settings.LANGUAGES (iso 639-1)
    to Postgres configuration names.
    e.g. "en" => "customized_english"
      or "nn" => "Norwegian Nynorsk" => "customized_norwegian"

    Our configurations, unlike the default configurations, have the
    prefix "customized_". They have the additional feature of removing
    accents.
    """
    if language_code in LANGUAGE_CODE_TO_NAME_MATCHING:
        full_language_name = LANGUAGE_CODE_TO_NAME_MATCHING[language_code]
        postgres_config_name = "customized_" + full_language_name.lower().split(" ")[0]
        if postgres_config_name in POSTGRES_SEARCH_CONFIGS:
            return postgres_config_name

    return DEFAULT_SEARCH_CONFIG
