"""Text summary statistics."""

from .helpers import clean, tokenize


def summarize(text):
    """Return word count, unique word count and average word length.

    The function follows the specification:
    * Words are split on any whitespace.
    * Leading/trailing punctuation defined in :data:`textstats.helpers.PUNCT`
      is removed.  Tokens that become empty after stripping are ignored.
    * Uniqueness is case‑insensitive.
    * ``avg_len`` is the mean length of the cleaned words, rounded to two
      decimals.  For an empty input or when no valid words remain it returns
      ``0.0`` and does not raise a division‑by‑zero error.
    """
    tokens = tokenize(text)
    cleaned = [clean(t) for t in tokens]
    # Filter out empty strings (tokens that were only punctuation).
    words = [c for c in cleaned if c]
    unique = len(set(w.lower() for w in words))
    if not words:
        avg_len = 0.0
    else:
        avg_len = round(sum(len(w) for w in words) / len(words), 2)
    return {"words": len(words), "unique": unique, "avg_len": avg_len}
