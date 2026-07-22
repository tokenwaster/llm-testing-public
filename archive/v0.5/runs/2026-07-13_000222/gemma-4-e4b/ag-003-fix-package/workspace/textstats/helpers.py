"""Tokenisation helpers for textstats."""

PUNCT = ".,;:!?\"'()"


def tokenize(text):
    """Split text into raw word tokens."""
    return text.split()


def clean(token):
    """Strip surrounding punctuation from a token."""
    # Ensure the input is treated as a string before stripping, although split() should guarantee this.
    if not isinstance(token, str):
        return ""
    return token.strip(PUNCT)