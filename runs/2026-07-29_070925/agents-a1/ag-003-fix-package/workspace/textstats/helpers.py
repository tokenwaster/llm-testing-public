import re

PUNCT = ".,;:!?'()"


def tokenize(text):
    return re.findall(r'\S+', text)


def clean(token):
    return token.strip(PUNCT)
