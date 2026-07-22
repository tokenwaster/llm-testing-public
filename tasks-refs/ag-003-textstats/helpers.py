"""Reference fix: split on ANY whitespace; clean lowercases + strips punct."""
PUNCT = ".,;:!?\"'()"


def tokenize(text):
    return text.split()


def clean(token):
    return token.strip(PUNCT).lower()
