PUNCT = ".,;:!?\"'()"


def tokenize(text):
    # Split on ANY whitespace (spaces, tabs, newlines, runs of them).
    return text.split()


def clean(token):
    # Strip leading/trailing punctuation and fold case so that
    # "Dog." and "dog" compare equal.
    return token.strip(PUNCT).lower()
