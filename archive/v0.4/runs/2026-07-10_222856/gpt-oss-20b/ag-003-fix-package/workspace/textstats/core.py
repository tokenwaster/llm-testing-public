"""Text summary statistics."""

from .helpers import clean, tokenize


def summarize(text):
    """Return word count, unique word count and average word length.

    Parameters
    ----------
    text : str
        Input string to analyse.

    Returns
    -------
    dict
        ``{"words": int, "unique": int, "avg_len": float}``
    """
    tokens = tokenize(text)
    cleaned = [clean(t) for t in tokens]
    # filter out empty strings (tokens that were only punctuation)
    words = [c for c in cleaned if c]
    unique = len(set(w.lower() for w in words))
    if not words:
        avg_len = 0.0
    else:
        avg_len = round(sum(len(w) for w in words) / len(words), 2)
    return {"words": len(words), "unique": unique, "avg_len": avg_len}
