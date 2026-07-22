"""Tokenisation helpers for textstats."""

PUNCT = ".,;:!?\"'()"


def tokenize(text):
    """Split text into raw word tokens."""
    # Use split() with no arguments to handle all whitespace types (spaces, tabs, newlines)
    # and multiple occurrences correctly.
    return text.split()


def clean(token):
    """Strip surrounding punctuation from a token."""
    return token.strip(PUNCT)