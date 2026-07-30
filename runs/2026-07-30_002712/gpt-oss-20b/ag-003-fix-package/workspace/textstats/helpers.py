
PUNCT = ".,;:!?\"'()"


def tokenize(text):
    """Split the text on any whitespace.

    The original implementation used ``text.split(" ")`` which only splits on
    literal spaces.  As a result tabs and newlines were treated as part of
    tokens, causing incorrect word counts.  Using ``str.split()`` without an
    argument performs the desired split on *any* whitespace.
    """
    return text.split()


def clean(token):
    """Strip leading and trailing punctuation defined in :data:`PUNCT`.

    The function is intentionally simple – it only removes the characters
    listed in ``PUNCT`` from both ends of the string.  Tokens that consist
    solely of punctuation will become an empty string, which callers can
    filter out.
    """
    return token.strip(PUNCT)
