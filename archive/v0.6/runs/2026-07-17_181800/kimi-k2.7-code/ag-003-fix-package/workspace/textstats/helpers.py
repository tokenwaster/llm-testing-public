import re


def clean(token: str) -> str | None:
    """Return lowercased word with leading/trailing punctuation removed.

    Returns None if the token contains no word characters.
    """
    cleaned = token.strip(".,;:!?\"'()")
    if not cleaned:
        return None
    return cleaned.lower()
