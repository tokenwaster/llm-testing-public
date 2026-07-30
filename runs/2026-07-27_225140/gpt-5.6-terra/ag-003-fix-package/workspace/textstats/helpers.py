PUNCT = ".,;:!?\"'()"


def tokenize(text):
    """Split text on arbitrary runs of whitespace."""
    return text.split()


def clean(token):
    """Remove boundary punctuation and normalize for comparison."""
    return token.strip(PUNCT).lower()
