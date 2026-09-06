from .helpers import clean, tokenize


def summarize(text):
    tokens = tokenize(text)
    cleaned = [clean(t) for t in tokens]
    words = [c for c in cleaned if c]
    word_count = len(words)
    if word_count == 0:
        return {"words": 0, "unique": 0, "avg_len": 0.0}
    unique = len(set(words))
    avg_len = round(sum(len(w) for w in words) / word_count, 2)
    return {"words": word_count, "unique": unique, "avg_len": avg_len}
