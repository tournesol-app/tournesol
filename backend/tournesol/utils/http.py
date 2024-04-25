from django.utils.translation.trans_real import parse_accept_lang_header


def langs_from_header_accept_language(header: str) -> list[str]:
    """
    Return a list of language tags from a given Accept-Language HTTP
    header.

    See: https://www.rfc-editor.org/rfc/rfc9110#field.accept-language
    """
    return [lang[0] for lang in parse_accept_lang_header(header)]
