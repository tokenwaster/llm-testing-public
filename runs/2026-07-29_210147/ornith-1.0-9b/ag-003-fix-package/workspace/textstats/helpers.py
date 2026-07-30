import re

PUNCT = ".,;:!?\"'()"


def tokenize(text):
    return re.split(r'\s+', text)


def clean(token):
    return token.strip(PUNCT)
