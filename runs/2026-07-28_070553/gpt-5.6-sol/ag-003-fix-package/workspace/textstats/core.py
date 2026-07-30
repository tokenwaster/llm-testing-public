from .helpers import clean, tokenize


def summarize(text):
    tokens = tokenize(text)
    words = [word for token in tokens if (word := clean(token))]

    if not words:
        return {"words": 0, "unique": 0, "avg_len": 0.0}

    unique = len({word.casefold() for word in words})
    avg_len = round(sum(len(word) for word in words) / len(words), 2)
    return {"words": len(words), "unique": unique, "avg_len": avg_len}
