"""Tokenisation helpers for textstats."""

import re

PUNCT = ".,;:!?\"'()"


def tokenize(text):
    """Split text into raw word tokens."""
    return re.split(r'\s+', text.strip()) if text.strip() else []


def clean(token):
    """Strip surrounding punctuation from a token."""
    return token.strip(PUNCT).lower()
