"""Tokenisation helpers for textstats."""

import re

PUNCT = ".,;:!?\"'()"


def tokenize(text):
    """Split text into raw word tokens on any whitespace."""
    return re.split(r"\s+", text)


def clean(token):
    """Strip surrounding punctuation from a token."""
    return token.strip(PUNCT)
