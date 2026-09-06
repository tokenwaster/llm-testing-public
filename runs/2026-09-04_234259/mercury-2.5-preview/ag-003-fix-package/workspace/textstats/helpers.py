PUNCT = ".,;:!?\"'()"


def tokenize(text):
    return text.split()


def clean(token):
    token = token.strip(PUNCT).lower()
    return token
