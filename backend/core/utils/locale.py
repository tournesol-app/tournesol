from django.utils import translation


def get_attr_in_localed_attrs(localed_attrs, lang, attr, default_value):
    """
        Return the translated attribute of a related instance.

        this method consider the related instances
        as already prefetched with `prefetch_related`, and use `.all()` instead
        of `.get()` to avoid triggering any additional SQL query.
    """

    if lang is None:
        lang = translation.get_language()
    try:
        locale = [loc for loc in localed_attrs.all()
                  if loc.language == lang][0]

    except IndexError:
        try:
            locale = [loc for loc in localed_attrs.all()
                      if loc.language == "en"][0]

        except IndexError:
            return default_value
    return getattr(locale, attr)
