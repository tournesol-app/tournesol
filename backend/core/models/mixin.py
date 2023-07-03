from django.core.exceptions import ObjectDoesNotExist
from django.utils import translation


class LocalizedFieldsMixin:
    """
    A mixin that can be inherited by all models having one or more relations that contain
    translated text.
    """

    def get_localized_text(self, related, field, lang=None, default=""):
        """
        Return the content of `field` from the related model `related`,
        translated in the language `lang`.
        """
        if lang is None:
            lang = translation.get_language()

        try:
            locale = getattr(self, related).get(language=lang)
        except ObjectDoesNotExist:
            try:
                locale = getattr(self, related).get(language="en")
            except ObjectDoesNotExist:
                return default

        return getattr(locale, field)

    def get_localized_text_prefetch(self, related, field, lang=None, default=""):
        """
        Contrary to `self.get_text` this method consider the related instances
        as already prefetched with `prefetch_related`, and use `.all()` instead
        of `.get()` to avoid triggering any additional SQL query.
        """
        if lang is None:
            lang = translation.get_language()

        try:
            locale = [loc for loc in getattr(self, related).all() if loc.language == lang][0]

        except IndexError:
            try:
                locale = [loc for loc in getattr(self, related).all() if loc.language == "en"][0]

            except IndexError:
                return default

        return getattr(locale, field)
