"""Text summary statistics."""

from .helpers import clean, tokenize


def summarize(text):
    """Return word count, unique word count and average word length."""
    tokens = tokenize(text)
    cleaned = [clean(t) for t in tokens]
    words = [c for c in cleaned if c]

    if not words:
        return {"words": 0, "unique": 0, "avg_len": 0.0}

    # Calculate unique count (case-insensitive)
    unique_lower = set(w.lower() for w in words)
    unique = len(unique_lower)

    word_count = len(words)
    total_length = sum(len(w) for w in words)
    avg_len = round(total_length / word_count, 2)

    return {"words": word_count, "unique": unique, "avg_len": avg_len}
