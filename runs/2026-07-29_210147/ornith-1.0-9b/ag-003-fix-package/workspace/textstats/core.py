from .helpers import clean, tokenize


def summarize(text):
    tokens = tokenize(text)
    cleaned = [clean(t).lower() for t in tokens]
    words = [w for w in cleaned if w]
    unique = len(set(words))
    avg_len = round(sum(len(w) for w in words) / len(words), 2) if words else 0.0
    return {"words": len(words), "unique": unique, "avg_len": avg_len}
