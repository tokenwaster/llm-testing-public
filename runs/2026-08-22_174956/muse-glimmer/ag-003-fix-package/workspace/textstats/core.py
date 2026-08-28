
from .helpers import clean, tokenize


def summarize(text):
    tokens = tokenize(text)
    cleaned = [clean(t) for t in tokens]
    # case-insensitive unique, and filter out empty tokens
    words_cleaned = []
    words_for_unique = []
    for c in cleaned:
        if not c:
            continue
        lower = c.lower()
        words_cleaned.append(lower)
        words_for_unique.append(lower)
    if not words_cleaned:
        return {"words": 0, "unique": 0, "avg_len": 0.0}
    words = len(words_cleaned)
    unique = len(set(words_for_unique))
    avg_len = round(sum(len(w) for w in words_cleaned) / words, 2)
    return {"words": words, "unique": unique, "avg_len": avg_len}
