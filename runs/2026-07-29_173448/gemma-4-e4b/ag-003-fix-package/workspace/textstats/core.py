
from .helpers import clean, tokenize


def summarize(text):
    tokens = tokenize(text)
    cleaned = [clean(t) for t in tokens]
    words = [c for c in cleaned if c]

    word_count = len(words)
    unique_count = len(set(words))

    if word_count == 0:
        return {"words": 0, "unique": 0, "avg_len": 0.0}

    total_length = sum(len(w) for w in words)
    avg_len = round(total_length / word_count, 2)
    
    return {"words": word_count, "unique": unique_count, "avg_len": avg_len}
