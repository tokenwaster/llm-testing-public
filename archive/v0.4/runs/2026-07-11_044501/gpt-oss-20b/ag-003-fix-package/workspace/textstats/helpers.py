"""Tokenisation helpers for textstats."""

# Characters considered punctuation for stripping around tokens.
PUNCT = ".,;:!?\"'()"


def tokenize(text):
    """Split *text* into raw word tokens using any whitespace as separator.

    The original implementation used ``str.split(" ")`` which only splits on
    literal spaces and fails to handle tabs, newlines or multiple consecutive
    separators.  ``str.split()`` without an argument splits on arbitrary runs of
    whitespace, matching the specification.
    """
    return text.split()


def clean(token):
    """Return *token* with surrounding punctuation removed.

    Tokens that consist solely of punctuation characters are considered empty
    after cleaning and should be ignored by :func:`summarize`.
    """
    # ``strip`` removes any leading or trailing characters in the set.
    return token.strip(PUNCT)
