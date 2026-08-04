
PUNCT = ".,;:!?\"'()"


def tokenize(text):
    # Split on any run of whitespace (spaces, tabs, newlines, ...).
    return text.split()


def clean(token):
    return token.strip(PUNCT)
