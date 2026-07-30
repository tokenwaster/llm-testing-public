"""Text summary statistics."""

from .helpers import clean, tokenize


def summarize(text):
    """Return word count, unique word count and average word length.

    - ``words``: total number of words after tokenisation, ignoring tokens that consist
      solely of punctuation.
    - ``unique``: number of distinct words, case‑insensitive and after stripping
      surrounding punctuation.
    - ``avg_len``: mean length of the cleaned words, rounded to two decimal places.
      For empty input (or input with no valid words) ``avg_len`` is ``0.0``.
    """
    # Tokenise on any whitespace.
    tokens = tokenize(text)
    # Clean each token by stripping surrounding punctuation.
    cleaned = [clean(t) for t in tokens]
    # Keep only non‑empty cleaned tokens – tokens that were only punctuation are ignored.
    words = [c for c in cleaned if c]
    # Unique count is case‑insensitive.
    unique = len({w.lower() for w in words})
    # Compute average length safely.
    if words:
        avg_len = round(sum(len(w) for w in words) / len(words), 2)
    else:
        avg_len = 0.0
    return {"words": len(words), "unique": unique, "avg_len": avg_len}
