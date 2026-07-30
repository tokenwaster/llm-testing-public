import re

def title_case(s: str) -> str:
    """Capitalize the first letter of each word, lowercase the rest.
    Words are separated by spaces; internal apostrophes stay untouched
    (``it's`` -> ``It's``, never ``It'S``)."""
    # BUG: str.title() capitalizes after apostrophes too ("it'S")
    # We want to capitalize words separated by spaces.
    words = s.split(' ')
    capitalized_words = []
    for word in words:
        if not word:
            capitalized_words.append(word)
            continue
        
        # Handle the first character of the word
        first_char = word[0].upper()
        # Handle the rest of the word
        rest_of_word = word[1:].lower()
        
        capitalized_words.append(first_char + rest_of_word)
        
    return " ".join(capitalized_words)


def snake_case(s: str) -> str:
    out = []
    for i, ch in enumerate(s):
        if ch.isupper() and i > 0 and (s[i - 1].islower()
                                       or (i + 1 < len(s)
                                           and s[i + 1].islower())):
            out.append("_")
        out.append(ch.lower())
    return "".join(out).replace(" ", "_").replace("-", "_")


def truncate(s: str, limit: int) -> str:
    """Cut to at most `limit` chars, appending an ellipsis character if cut."""
    if len(s) <= limit:
        return s
    return s[: max(limit - 1, 0)] + "…"
