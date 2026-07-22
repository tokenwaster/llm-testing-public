"""Text summary statistics."""

from .helpers import clean, tokenize


def summarize(text):
    """Return word count, unique word count and average word length."""
    cleaned = [clean(token) for token in tokenize(text)]
    words = [word for word in cleaned if word]
    if not words:
        return {"words": 0, "unique": 0, "avg_len": 0.0}

    # Word identity is case-insensitive, while lengths are those of the
    # cleaned words as supplied.
    unique = len({word.casefold() for word in words})
    avg_len = round(sum(len(word) for word in words) / len(words), 2)
    return {"words": len(words), "unique": unique, "avg_len": avg_len}
