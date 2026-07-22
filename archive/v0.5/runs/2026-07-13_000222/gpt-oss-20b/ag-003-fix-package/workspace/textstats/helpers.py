"""Tokenisation helpers for textstats."""

PUNCT = ".,;:!?\"'()"

def tokenize(text):
    """Split text into raw word tokens using any whitespace."""
    # split on any whitespace sequence
    return text.split()

def clean(token):
    """Strip surrounding punctuation from a token."""
    return token.strip(PUNCT)
