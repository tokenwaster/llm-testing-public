from .helpers import clean, tokenize


def summarize(text):
    tokens = tokenize(text)
    cleaned = [clean(t) for t in tokens]
    words = [c for c in cleaned if c]  # punctuation-only tokens are not words
    if not words:
        return {"words": 0, "unique": 0, "avg_len": 0.0}
    unique = len({w.lower() for w in words})  # case-insensitive uniqueness
    avg_len = round(sum(len(w) for w in words) / len(words), 2)
    return {"words": len(words), "unique": unique, "avg_len": avg_len}
