
PUNCT = ".,;:!?\"'()"


def tokenize(text):
    # Use split() without arguments to handle any sequence of whitespace (spaces, tabs, newlines) 
    # and automatically filter out empty tokens resulting from multiple delimiters.
    return text.split()


def clean(token):
    # Strip leading/trailing punctuation AND convert to lowercase for case-insensitive uniqueness.
    return token.strip(PUNCT).lower()
