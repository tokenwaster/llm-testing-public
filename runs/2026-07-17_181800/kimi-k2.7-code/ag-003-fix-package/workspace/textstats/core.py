from .helpers import clean


def summarize(text: str) -> dict:
    raw_tokens = text.split()
    words = []
    for token in raw_tokens:
        cleaned = clean(token)
        if cleaned is not None:
            words.append(cleaned)

    if not words:
        return {"words": 0, "unique": 0, "avg_len": 0.0}

    return {
        "words": len(words),
        "unique": len(set(words)),
        "avg_len": round(sum(len(w) for w in words) / len(words), 2),
    }
