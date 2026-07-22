"""Tokenisation helpers for textstats."""

PUNCT = ".,;:!?\"'()"


def tokenize(text):
    """Split text into raw word tokens on any whitespace."""
    return text.split()


def clean(token):
    """Strip the specified surrounding punctuation from a token."""
    return token.strip(PUNCT)
