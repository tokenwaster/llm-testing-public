"""Text summary statistics."""

from .helpers import clean, tokenize

def summarize(text):
    """Return word count, unique word count and average word length.

    Words are separated by any whitespace.  Punctuation is stripped from the
    beginning and end of each token; tokens that become empty after stripping
    are ignored entirely.  Unique words are counted case‑insensitively.
    """
    tokens = tokenize(text)
    cleaned = [clean(t) for t in tokens]
    # Filter out empty strings (tokens that were only punctuation)
    words = [c for c in cleaned if c]
    if not words:
        return {"words": 0, "unique": 0, "avg_len": 0.0}
    # Unique count is case‑insensitive
    unique = len(set(w.lower() for w in words))
    avg_len = round(sum(len(w) for w in words) / len(words), 2)
    return {"words": len(words), "unique": unique, "avg_len": avg_len}
