import re

PUNCT = ".,;:!?\"'()"

_WS_RE = re.compile(r"\s+")


def tokenize(text):
    return _WS_RE.split(text.strip())


def clean(token):
    return token.strip(PUNCT)
