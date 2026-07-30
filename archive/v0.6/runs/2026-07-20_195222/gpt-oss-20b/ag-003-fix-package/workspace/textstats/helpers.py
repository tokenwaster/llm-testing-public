"""Tokenisation helpers for textstats."""

# Characters considered punctuation for stripping
PUNCT = ".,;:!?\"'()"


def tokenize(text):
    """Split text into raw word tokens using any whitespace.

    The built‑in ``str.split`` without arguments splits on arbitrary runs of
    whitespace (spaces, tabs, newlines).  This matches the specification.
    """
    return text.split()


def clean(token):
    """Strip surrounding punctuation from a token.

    Tokens that consist solely of punctuation are returned as an empty string
    so they can be filtered out later.  The function is case‑insensitive for
    the purpose of counting unique words, but we keep the original case here
    and normalise in ``summarize``.
    """
    return token.strip(PUNCT)
