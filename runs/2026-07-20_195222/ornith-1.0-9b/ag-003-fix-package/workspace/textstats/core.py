"""Text summary statistics."""

from .helpers import clean, tokenize


def summarize(text):
    """Return word count, unique word count and average word length."""
    tokens = tokenize(text)
    cleaned = [clean(t) for t in tokens]
    words = [c for c in cleaned if c]
    # Case-insensitive uniqueness: lowercase for comparison
    unique_words = set(w.lower() for w in words)
    avg_len = round(sum(len(w) for w in words) / len(words), 2) if words else 0.0
    return {"words": len(words), "unique": len(unique_words), "avg_len": avg_len}
