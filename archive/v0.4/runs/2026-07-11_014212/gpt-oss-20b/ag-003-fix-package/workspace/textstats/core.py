"""Text summary statistics."""

from .helpers import clean, tokenize


def summarize(text):
    """Return word count, unique word count and average word length.

    Handles empty input gracefully.  Words are split on any whitespace,
    cleaned of surrounding punctuation, and counted case‑insensitively for the
    ``unique`` metric.
    """
    tokens = tokenize(text)
    cleaned = [clean(t) for t in tokens]
    words = [c for c in cleaned if c]  # ignore pure punctuation
    word_count = len(words)
    unique = len(set(w.lower() for w in words))
    avg_len = round(sum(len(w) for w in words) / word_count, 2) if word_count else 0.0
    return {"words": word_count, "unique": unique, "avg_len": avg_len}
