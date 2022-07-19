import re
from collections import Counter

from django.conf import settings
from langdetect import DetectorFactory, detect, lang_detect_exception

from ..models.entity import Entity

LANGUAGE_CODE_TO_NAME_MATCHING = dict(settings.LANGUAGES)
ACCEPTED_LANGUAGE_CODES = set(LANGUAGE_CODE_TO_NAME_MATCHING.keys())


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
