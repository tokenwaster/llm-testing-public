"""Tokenisation helpers for textstats."""

# Characters considered punctuation for stripping
PUNCT = ".,;:!?\"'()"


def tokenize(text):
    """Split text into raw word tokens using any whitespace as separator.
    ``str.split`` without arguments splits on arbitrary runs of whitespace and
    also handles newlines/tabs.  It returns an empty list for an empty string.
    """
    return text.split()


def clean(token):
    """Strip surrounding punctuation from a token.
    ``str.strip`` removes only the characters in *PUNCT* from both ends of the
    string.  It does not modify internal punctuation.
    """
    return token.strip(PUNCT)
