"""Tokenisation helpers for textstats."""

PUNCT = ".,;:!?\"'()"

def tokenize(text):
    """Split text into raw word tokens."""
    return text.split()

def clean(token):
    """Strip surrounding punctuation and lowercase."""
    return token.strip(PUNCT).lower()