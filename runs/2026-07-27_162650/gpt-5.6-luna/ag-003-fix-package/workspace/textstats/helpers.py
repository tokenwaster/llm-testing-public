PUNCT = ".,;:!?\"'()"


def tokenize(text):
    """Split *text* into tokens separated by any whitespace."""
    return text.split()


def clean(token):
    """Remove the specified punctuation from both ends of a token."""
    return token.strip(PUNCT)
