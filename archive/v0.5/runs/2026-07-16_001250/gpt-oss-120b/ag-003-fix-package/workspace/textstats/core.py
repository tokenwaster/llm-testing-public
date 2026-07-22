"""Text summary statistics."""

from .helpers import clean, tokenize


def summarize(text):
    """Return word count, unique word count and average word length.

    The function follows the specification:
    * Words are tokens obtained by splitting on any whitespace.
    * Tokens consisting solely of punctuation are ignored.
    * Punctuation defined in ``helpers.PUNCT`` is stripped from the start and
      end of each token.
    * Word comparison is case‑insensitive.
    * ``avg_len`` is the mean length of the cleaned words, rounded to two
      decimal places. For empty input the average is ``0.0``.
    """
    # Tokenise on any whitespace.
    tokens = tokenize(text)
    # Clean each token and filter out empty results.
    cleaned = [clean(t) for t in tokens]
    # Keep only non‑empty tokens and normalise case for counting.
    words = [c.lower() for c in cleaned if c]
    # Total word count.
    total = len(words)
    # Unique word count (case‑insensitive).
    unique = len(set(words))
    # Average length, handling the empty case.
    if total:
        avg_len = round(sum(len(w) for w in words) / total, 2)
    else:
        avg_len = 0.0
    return {"words": total, "unique": unique, "avg_len": avg_len}
