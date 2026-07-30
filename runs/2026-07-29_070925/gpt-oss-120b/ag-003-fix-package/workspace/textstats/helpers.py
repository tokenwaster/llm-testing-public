
PUNCT = ".,;:!?\"'()"


def tokenize(text):
    """Split text into tokens using any whitespace.

    This mirrors ``str.split`` with no separator argument, which treats runs of
    spaces, tabs, newlines, etc., as delimiters and discards empty results.
    """
    # Using the default split behavior splits on arbitrary whitespace and
    # collapses consecutive whitespace characters.
    return text.split()


def clean(token):
    """Strip leading and trailing punctuation defined in :data:`PUNCT`."""
    return token.strip(PUNCT)
