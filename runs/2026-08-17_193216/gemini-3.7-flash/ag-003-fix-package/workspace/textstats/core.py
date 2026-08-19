from .helpers import clean, tokenize


def summarize(text: str) -> dict:
    tokens = tokenize(text)
    cleaned_words = []
    for token in tokens:
        cleaned = clean(token)
        if cleaned:
            cleaned_words.append(cleaned)

    if not cleaned_words:
        return {"words": 0, "unique": 0, "avg_len": 0.0}

    words_count = len(cleaned_words)
    unique_count = len({w.lower() for w in cleaned_words})
    avg_len = round(sum(len(w) for w in cleaned_words) / words_count, 2)

    return {
        "words": words_count,
        "unique": unique_count,
        "avg_len": avg_len,
    }
