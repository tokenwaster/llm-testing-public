"""Tokenisation helpers for textstats."""

PUNCT = ".,;:!?\"'()"


def tokenize(text):
    """Split text into raw word tokens."""
    return text.split()


def clean(token):
    """Strip surrounding punctuation from a token and lower-case it."""
    return token.strip(PUNCT).lower()
