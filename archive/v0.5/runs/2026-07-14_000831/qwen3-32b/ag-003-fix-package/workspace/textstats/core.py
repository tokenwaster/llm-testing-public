"""Text summary statistics."""

from .helpers import clean, tokenize

def summarize(text):
    tokens = tokenize(text)
    cleaned = [clean(t) for t in tokens]
    words = [c for c in cleaned if c]
    unique = len(set(words))
    avg_len = 0.0\n    if words:\n        avg_len = round(sum(len(w) for w in words) / len(words), 2)\n    return {"words": len(words), "unique": unique, "avg_len": avg_len}