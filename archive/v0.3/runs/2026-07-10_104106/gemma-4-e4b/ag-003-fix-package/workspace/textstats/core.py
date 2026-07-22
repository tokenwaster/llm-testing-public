"""Text summary statistics."""

from .helpers import clean, tokenize


def summarize(text):
    """Return word count, unique word count and average word length."""
    if not text:
        return {"words": 0, "unique": 0, "avg_len": 0.0}

    tokens = tokenize(text)
    
    # Clean tokens and convert to lowercase immediately
    cleaned_lower = []
    for t in tokens:
        c = clean(t)
        if c: # Only keep non-empty strings (i.e., not pure punctuation)
            cleaned_lower.append(c.lower())

    words = cleaned_lower
    
    # Calculate metrics
    word_count = len(words)
    unique_count = len(set(words))
    
    if word_count == 0:
        avg_len = 0.0
    else:
        total_length = sum(len(w) for w in words)
        avg_len = round(total_length / word_count, 2)
        
    return {"words": word_count, "unique": unique_count, "avg_len": avg_len}