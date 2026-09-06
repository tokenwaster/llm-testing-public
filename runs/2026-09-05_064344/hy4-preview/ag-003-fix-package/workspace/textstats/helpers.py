PUNCT = ".,;:!?\"'()"


def tokenize(text):
    """Split text on any whitespace, discarding empty tokens."""
    return text.split()


def clean(token):
    """Strip leading/trailing punctuation and lowercase for comparison."""
    return token.strip(PUNCT).lower()
