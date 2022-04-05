from rest_registration.utils.html import convert_html_to_text_preserving_urls


def html_to_text(value: str):
    text = convert_html_to_text_preserving_urls(value)
    # Workaround buggy conversion from "&timestamp" to "×tamp"
    return text.replace("×", "&times")
