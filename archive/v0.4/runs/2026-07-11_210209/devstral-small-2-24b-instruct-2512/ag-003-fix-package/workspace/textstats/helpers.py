"""Tokenisation helpers for textstats."""

import re

PUNCT = ".,;:!?\"'()"


def tokenize(text):
    """Split text into raw word tokens using any whitespace."""
    # Split on any whitespace (spaces, tabs, newlines, etc.)
    return re.split(r'\s+', text)


def clean(token):
    """Strip surrounding punctuation from a token and convert to lowercase."""
    if not token:
        return ""
    # Strip punctuation and convert to lowercase
    cleaned = token.strip(PUNCT).lower()
    return cleaned
