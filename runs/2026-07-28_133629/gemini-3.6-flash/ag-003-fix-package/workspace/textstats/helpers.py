PUNCTUATION = '.,;:!?"\'()'

def clean(token: str) -> str:
    return token.strip(PUNCTUATION).lower()
