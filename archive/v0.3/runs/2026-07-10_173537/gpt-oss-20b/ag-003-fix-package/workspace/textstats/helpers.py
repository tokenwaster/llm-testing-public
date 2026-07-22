"""Tokenisation helpers for textstats."""

# Characters considered punctuation for stripping
PUNCT = ".,;:!?\"'()"


def tokenize(text):
    """Split text into raw word tokens.

    The specification requires splitting on any whitespace (spaces, tabs,
    newlines, multiple in a row). Python's ``str.split`` without an argument
    already does exactly that – it splits on arbitrary runs of whitespace and
    discards empty strings.  Using ``split(" ")`` would only split on literal
    spaces and keep other whitespace characters as part of tokens.
    """
    return text.split()


def clean(token):
    """Strip surrounding punctuation from a token.

    Only leading and trailing punctuation defined in ``PUNCT`` is removed.  The
    function returns the cleaned string; if the result is an empty string it
    represents a token that was only punctuation.
    """
    return token.strip(PUNCT)
