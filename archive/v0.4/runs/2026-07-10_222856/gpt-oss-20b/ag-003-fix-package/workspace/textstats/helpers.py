"""Tokenisation helpers for textstats."""

import string

# Define punctuation set: . , ; : ! ? " ' ( )
PUNCT = ".,;:!?\"'()"


def tokenize(text):
    """Split text into raw word tokens using any whitespace.
    ``str.split`` without arguments splits on arbitrary runs of whitespace.
    """
    return text.split()


def clean(token):
    """Strip surrounding punctuation from a token.
    Returns the cleaned token; if the result is empty (token was only punctuation)
    an empty string is returned.
    """
    # strip both leading and trailing punctuation defined in PUNCT
    return token.strip(PUNCT)
