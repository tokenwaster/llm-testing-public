
from .helpers import clean, tokenize


def summarize(text):
    """Summarize the given text.

    Returns a dictionary with total word count, number of unique words (case-
    insensitive, punctuation stripped), and the average length of the cleaned
    words rounded to two decimal places.
    """
    tokens = tokenize(text)
    # Clean each token and discard empty results (tokens that were only
    # punctuation). Convert to lower case for case‑insensitive uniqueness.
    cleaned = [clean(t).lower() for t in tokens]
    words = [c for c in cleaned if c]
    unique = len(set(words))
    if words:
        avg_len = round(sum(len(w) for w in words) / len(words), 2)
    else:
        avg_len = 0.0
    return {"words": len(words), "unique": unique, "avg_len": avg_len}
