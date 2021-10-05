"""
TODO: verifies this module and possibly re-enable its use
Old comment about this file: 'Unused, using SQL queries now'
"""

from fuzzysearch import find_near_matches


class VideoSearchEngine(object):
    """Score videos by phrases and by the preferences."""

    # set once per thread
    search_phrase = None
    user_features = None
    VIDEO_SEARCH_COEFF = 1000 * 5

    @staticmethod
    def set_parameters(search_phrase, user_preferences):
        """Set search parameters."""
        VideoSearchEngine.search_phrase = search_phrase
        VideoSearchEngine.user_features = user_preferences.features_as_vector_centered

    @staticmethod
    def _fuzzysearch_score_fcn(v_text, phrase, max_l_dist=1):
        """Fuzzy search score function."""
        if v_text is None:
            return -9999

        matches = find_near_matches(
            phrase.lower(), v_text.lower(), max_l_dist=max_l_dist
        )

        return sum([1 - 1.0 * m.dist / (max_l_dist + 1) for m in matches])

    @staticmethod
    def score(v_text, v_features, video_search_phrase_coeff=VIDEO_SEARCH_COEFF):
        """Default score function (fuzzy)."""
        result = {}
        eng = VideoSearchEngine
        result["preferences_term"] = (
            (eng.user_features @ v_features) if (eng.user_features is not None) else 0.0
        )
        result["phrase_term"] = (
            eng._fuzzysearch_score_fcn(v_text, eng.search_phrase)
            if (eng.search_phrase is not None and eng.search_phrase)
            else 0.0
        )
        result["phrase_term"] *= video_search_phrase_coeff

        return result
