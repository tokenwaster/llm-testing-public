"""Text summary statistics."""

from .helpers import clean, tokenize


def summarize(text):
    """Return word count, unique word count and average word length."""
    tokens = tokenize(text)
    cleaned_words = []
    for t in tokens:
        c = clean(t)
        if c: # Only keep non-empty strings (i.e., actual words)
            cleaned_words.append(c)

    num_words = len(cleaned_words)

    if num_words == 0:
        return {"words": 0, "unique": 0, "avg_len": 0.0}

    # Case-insensitive unique count
    lower_words = [w.lower() for w in cleaned_words]
    num_unique = len(set(lower_words))

    # Average length calculation
    total_length = sum(len(w) for w in cleaned_words)
    avg_len = round(total_length / num_words, 2)

    return {"words": num_words, "unique": num_unique, "avg_len": avg_len}