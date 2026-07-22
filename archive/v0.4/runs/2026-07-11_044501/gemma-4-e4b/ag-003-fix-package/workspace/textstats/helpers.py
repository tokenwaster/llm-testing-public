"""Tokenisation helpers for textstats."""

# Punctuation characters specified: .,;:!?"'()
PUNCT = ".,;:!?\"'()"


def tokenize(text):
    """Split text into raw word tokens, handling all whitespace types."""
    # Using split() with no arguments handles spaces, tabs, newlines, and multiple occurrences.
    return text.split()


def clean(token):
    """Strip surrounding punctuation from a token."""
    return token.strip(PUNCT)