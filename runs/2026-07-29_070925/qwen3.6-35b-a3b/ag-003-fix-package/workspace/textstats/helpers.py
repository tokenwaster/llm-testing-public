PUNCT = ".,;:!?"'()"


def tokenize(text):
    return text.split()


def clean(token):
    stripped = token.strip(PUNCT)
    return stripped.lower()
