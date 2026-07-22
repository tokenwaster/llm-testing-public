"""Tokenisation helpers for textstats."""

PUNCT = ".,;:!?\"'()"


def tokenize(text):
    """Split text into raw word tokens."""
    # Use default split() to handle all whitespace types (spaces, tabs, newlines)
    return text.split()


def clean(token):
    """Strip surrounding punctuation from a token."""
    return token.strip(PUNCT)
