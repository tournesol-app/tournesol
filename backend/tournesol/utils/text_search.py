import re


def build_prefix_tsquery(text):
    """Build a tsquery string: 'climate chan' -> 'climate & chan:*'."""
    cleaned = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    words = cleaned.split()
    if not words:
        return ""
    words[-1] += ":*"
    return " & ".join(words)
