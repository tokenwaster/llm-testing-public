
PUNCT = ".,;:!?\"'()"


def tokenize(text):
    return text.split(" ")


def clean(token):
    return token.strip(PUNCT)
