from django.core.exceptions import ObjectDoesNotExist
from django.utils import translation


class GetText:
    def get_localized_text(self, field, related, lang=None,):
        if lang is None:
            lang = translation.get_language()

        is_faq = related in ('questions', 'answers')

        try:
            locale = getattr(self, related).get(language=lang)
        except ObjectDoesNotExist:
            try:
                locale = getattr(self, related).get(language="en")
            except ObjectDoesNotExist:
                if is_faq:
                    return self.name  # pylint: disable=no-member
                return ""
        return getattr(locale, field)

    def get_localized_text_prefetch(self, field, related, lang=None):
        """
        Contrary to `self.get_text` this method consider the related instances
        as already prefetched with `prefetch_related`, and use `.all()` instead
        of `.get()` to avoid triggering any additional SQL query.
        """
        if lang is None:
            lang = translation.get_language()

        is_faq = related in ('questions', 'answers')

        try:
            locale = [loc for loc in getattr(self, related).all()
                      if loc.language == lang][0]

        except IndexError:
            try:
                locale = [loc for loc in getattr(self, related).all()
                          if loc.language == "en"][0]

            except IndexError:
                if is_faq:
                    return self.name  # pylint: disable=no-member
                return ""
        return getattr(locale, field)
