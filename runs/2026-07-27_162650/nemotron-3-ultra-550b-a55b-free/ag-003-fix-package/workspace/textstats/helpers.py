import re

PUNCT = ".,;:!?\"'()[]"


def tokenize(text):
    # Split on any whitespace (spaces, tabs, newlines, multiple in a row)
    return text.split()


def clean(token):
    # Strip punctuation and convert to lowercase
    cleaned = token.strip(PUNCT)
    return cleaned.lower()