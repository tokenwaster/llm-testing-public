from .helpers import clean, tokenize


def summarize(text: str) -> dict:
    tokens = tokenize(text)
    cleaned = [clean(t) for t in tokens]
    words = [word for word in cleaned if word]
    if not words:
        return {"words": 0, "unique": 0, "avg_len": 0.0}

    # Case-insensitive uniqueness; preserve cleaned spelling for length.
    unique = len({word.casefold() for word in words})
    avg_len = round(sum(len(word) for word in words) / len(words), 2)
    return {"words": len(words), "unique": unique, "avg_len": avg_len}
