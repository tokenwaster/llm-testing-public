"""Text summary statistics."""

from .helpers import clean, tokenize


def summarize(text):
    """Return word count, unique word count and average word length."""
    tokens = tokenize(text)
    cleaned = [clean(t) for t in tokens]
    words = [c for c in cleaned if c]
    
    if not words:
        return {"words": 0, "unique": 0, "avg_len": 0.0}
    
    # Case-insensitive unique count
    unique = len(set(w.lower() for w in words))
    avg_len = round(sum(len(w) for w in words) / len(words), 2)
    return {"words": len(words), "unique": unique, "avg_len": avg_len}
