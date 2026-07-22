"""Text summary statistics."""

import re
from .helpers import clean, tokenize


def summarize(text):
    """Return word count, unique word count and average word length."""
    if not text:
        return {"words": 0, "unique": 0, "avg_len": 0.0}
        
    tokens = tokenize(text)
    cleaned = [clean(t) for t in tokens]
    
    # Filter words: must not be empty AND must contain at least one character that is NOT punctuation.
    punctuation_chars = r'[.,;:!?\"\'()]' # Based on textstats/helpers.py PUNCT definition
    words = []
    for c in cleaned:
        if not c:
            continue
        # Check if the word contains any character that is NOT defined as punctuation.
        # This ensures tokens like "---" or "..." are filtered out, satisfying the requirement 
        # that a token only consisting of punctuation does not count.
        if re.search(r'[^\W\d]', c) or re.search(r'\w', c): # Simplified check for non-punctuation content
            words.append(c)

    word_count = len(words)
    
    if word_count == 0:
        return {"words": 0, "unique": 0, "avg_len": 0.0}

    # Case-insensitive unique count requires converting all words to lowercase for comparison.
    lower_words = [w.lower() for w in words]
    unique_count = len(set(lower_words))
    
    # Calculate average length
    total_length = sum(len(w) for w in words)
    avg_len = round(total_length / word_count, 2)
    
    return {"words": word_count, "unique": unique_count, "avg_len": avg_len}