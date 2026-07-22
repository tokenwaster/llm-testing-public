"""Tokenisation helpers for textstats."""

# Characters considered as surrounding punctuation to strip.
PUNCT = ".,;:!?\"'()"


def tokenize(text):
    """Split text into raw word tokens using any whitespace as separator.

    The built‑in ``str.split`` without arguments splits on arbitrary runs of
    whitespace (spaces, tabs, newlines).  This matches the specification.
    """
    return text.split()


def clean(token):
    """Strip surrounding punctuation from a token and lower‑case it.

    The function removes any leading or trailing characters that are in
    :data:`PUNCT`.  It does *not* remove internal punctuation because the
    specification only requires stripping at the boundaries.  Lower‑casing is
    performed here so that ``unique`` can simply use a set of cleaned tokens.
    """
    return token.strip(PUNCT).lower()
