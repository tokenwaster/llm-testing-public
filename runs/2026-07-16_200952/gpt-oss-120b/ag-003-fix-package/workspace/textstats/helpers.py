"""Tokenisation helpers for textstats."""

PUNCT = ".,;:!?\"'()"


def tokenize(text):
    """Split text into raw word tokens.

    Uses any whitespace as delimiter, matching the specification.
    """
    # str.split() without arguments splits on any whitespace and discards empty strings.
    return text.split()


def clean(token):
    """Strip surrounding punctuation from a token.

    Returns the token with leading and trailing punctuation removed.
    """
    return token.strip(PUNCT)
