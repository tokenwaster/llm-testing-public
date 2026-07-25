"""Tokenisation helpers for textstats."""

PUNCT = ".,;:!?\"'()"


def tokenize(text):
    """Split text into raw word tokens.

    Words are separated by any run of whitespace (spaces, tabs,
    newlines, multiples in a row).
    """
    return text.split()


def clean(token):
    """Strip surrounding punctuation from a token and lowercase it.

    Comparison is case-insensitive, so the cleaned form is lowercased;
    a token that is only punctuation cleans to the empty string.
    """
    return token.strip(PUNCT).lower()
