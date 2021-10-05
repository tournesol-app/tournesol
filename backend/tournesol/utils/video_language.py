from collections import Counter
from langdetect import detect, lang_detect_exception
import re
from ..models import Video


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
    lang_list = Video.objects.filter(uploader=uploader).values_list("language")

    if lang_list:
        main_uploader_lang, main_uploader_lang_cnt = Counter(lang_list).most_common()[0]
        if len(lang_list) > 4 and main_uploader_lang_cnt/len(lang_list) > 0.9:
            return main_uploader_lang[0]

    return languages_detection(title, description)
