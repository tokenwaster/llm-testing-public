from .helpers import clean, tokenize


def summarize(text):
    tokens = tokenize(text)
    words = [c for c in (clean(t) for t in tokens) if c]
    if not words:
        return {"words": 0, "unique": 0, "avg_len": 0.0}
    avg_len = round(sum(len(w) for w in words) / len(words), 2)
    return {"words": len(words), "unique": len(set(words)), "avg_len": avg_len}
