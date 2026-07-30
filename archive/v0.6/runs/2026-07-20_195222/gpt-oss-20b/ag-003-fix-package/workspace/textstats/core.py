"""Text summary statistics."""

from .helpers import clean, tokenize


def summarize(text):
    """Return word count, unique word count and average word length.

    The function follows the specification: words are split on any whitespace,
    punctuation is stripped from each token, tokens that become empty after
    stripping are ignored, and uniqueness is counted case‑insensitively.
    """
    # Tokenise using any whitespace
    raw_tokens = tokenize(text)
    cleaned = [clean(t) for t in raw_tokens]
    # Filter out empty strings (punctuation only tokens)
    words = [c for c in cleaned if c]
    if not words:
        return {"words": 0, "unique": 0, "avg_len": 0.0}
    # Count unique case‑insensitive words
    unique = len(set(w.lower() for w in words))
    avg_len = round(sum(len(w) for w in words) / len(words), 2)
    return {"words": len(words), "unique": unique, "avg_len": avg_len}
