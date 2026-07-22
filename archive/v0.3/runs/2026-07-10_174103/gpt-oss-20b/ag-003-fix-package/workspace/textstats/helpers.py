"""Tokenisation helpers for textstats."""

# Characters considered as surrounding punctuation to strip.
PUNCT = ".,;:!?\"'()"

def tokenize(text):
    """Split text into raw word tokens using any whitespace as separator."""
    return text.split()

def clean(token):
    """Strip surrounding punctuation from a token.

    The function removes only leading and trailing characters that are in the
    :data:`PUNCT` set.  It does not modify internal punctuation such as an
    apostrophe inside ``can't``.
    """
    return token.strip(PUNCT)
