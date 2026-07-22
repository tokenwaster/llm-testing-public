"""Tokenisation helpers for textstats."""

PUNCT = ".,;:!?\"'()"

def tokenize(text):
    """Split text into raw word tokens using any whitespace as separator."""
    return text.split()

def clean(token):
    """Strip surrounding punctuation from a token."""
    return token.strip(PUNCT)
