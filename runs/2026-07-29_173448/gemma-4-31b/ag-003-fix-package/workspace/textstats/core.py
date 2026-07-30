
from .helpers import clean, tokenize


def summarize(text):
    tokens = tokenize(text)
    # Case-insensitive cleaning: lower the case before or after stripping punct?
    # Spec says "distinct words, case-insensitive, ignoring leading and trailing punctuation"
    # "Dog." and "dog" are same word.
    cleaned = [clean(t).lower() for t in tokens]
    words = [c for c in cleaned if c]
    
    if not words:
        return {"words": 0, "unique": 0, "avg_len": 0.0}
    
    unique = len(set(words))
    avg_len = round(sum(len(w) for w in words) / len(words), 2)
    return {"words": len(words), "unique": unique, "avg_len": avg_len}
