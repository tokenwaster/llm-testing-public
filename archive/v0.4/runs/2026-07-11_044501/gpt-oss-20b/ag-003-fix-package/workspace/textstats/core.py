"""Text summary statistics."""

from .helpers import clean, tokenize

def summarize(text):
    """Return word count, unique word count and average word length.

    The original implementation did not handle empty input or multiple
    whitespace correctly.  It also counted words case‑sensitively and raised a
    ``ZeroDivisionError`` when there were no words.
    """
    tokens = tokenize(text)
    cleaned = [clean(t) for t in tokens]
    # Keep only non‑empty cleaned tokens (pure punctuation is discarded).
    words = [c for c in cleaned if c]
    unique = len(set(w.lower() for w in words))
    avg_len = round(sum(len(w) for w in words) / len(words), 2) if words else 0.0
    return {"words": len(words), "unique": unique, "avg_len": avg_len}
