"""Text summary statistics."""

from .helpers import clean, tokenize


def summarize(text):
    """Return word count, unique word count and average word length."""
    tokens = tokenize(text)
    cleaned = [clean(t) for t in tokens]
    # Filter out empty strings (tokens that were only punctuation)
    words = [c for c in cleaned if c]

    if not words:
        return {"words": 0, "unique": 0, "avg_len": 0.0}

    # Case-insensitive unique count requires converting to lowercase
    lower_words = [w.lower() for w in words]
    unique = len(set(lower_words))

    # Calculate average length based on the cleaned word lengths
    total_length = sum(len(w) for w in words)
    avg_len = round(total_length / len(words), 2)

    return {"words": len(words), "unique": unique, "avg_len": avg_len}