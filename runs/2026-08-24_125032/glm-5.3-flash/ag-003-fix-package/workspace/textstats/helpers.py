PUNCT = ".,;:!?\"'()"


def tokenize(text):
    # Split on any whitespace (spaces, tabs, newlines) and drop empties.
    return text.split()


def clean(token):
    return token.strip(PUNCT)
