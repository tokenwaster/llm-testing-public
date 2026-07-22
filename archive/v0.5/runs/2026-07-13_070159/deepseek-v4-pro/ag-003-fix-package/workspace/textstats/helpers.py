"""Tokenisation helpers for textstats."""

PUNCT = ".,;:!?\"'()"


def tokenize(text):
    """Split text into raw word tokens on any whitespace."""
    return text.split()


def clean(token):
    """Strip surrounding punctuation from a token and lowercase it."""
    return token.strip(PUNCT).lower()