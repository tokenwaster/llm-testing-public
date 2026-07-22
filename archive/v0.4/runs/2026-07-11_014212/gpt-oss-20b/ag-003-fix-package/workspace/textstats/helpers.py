"""Tokenisation helpers for textstats."""

import string

# punctuation characters to strip from tokens (leading/trailing)
PUNCT = ".,;:!?\"'()"


def tokenize(text):
    """Split text into raw word tokens using any whitespace as separator.

    The original implementation used ``text.split(" ")`` which only splits on
    literal spaces.  This caused words separated by tabs or newlines to be
    treated as a single token.  ``str.split()`` without an argument splits on
    *any* whitespace and collapses consecutive separators, matching the
    specification.
    """
    return text.split()


def clean(token):
    """Strip surrounding punctuation from a token.

    Tokens that consist solely of punctuation become ``""`` after stripping and
    are ignored by :func:`summarize`.
    """
    return token.strip(PUNCT)
