"""Tokenisation helpers for textstats."""

PUNCT = ".,;:!?\"'()"


def tokenize(text):
    """Split text into raw word tokens.

    The specification requires splitting on any whitespace (spaces, tabs,
    newlines, etc.) and treating consecutive whitespace as a single separator.
    Using ``str.split()`` without an argument provides exactly that behaviour.
    """
    # ``split()`` with no separator splits on arbitrary runs of whitespace.
    return text.split()


def clean(token):
    """Strip surrounding punctuation from a token.

    Leading and trailing characters defined in ``PUNCT`` are removed. The
    function returns the cleaned token unchanged (case is handled later).
    """
    return token.strip(PUNCT)
