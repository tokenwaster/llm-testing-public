def title_case(s: str) -> str:
    """Capitalize the first letter of each word, lowercase the rest.
    Words are separated by spaces; internal apostrophes stay untouched
    (``it's`` -> ``It's``, never ``It'S``)."""
    # BUG: str.title() capitalizes after apostrophes too ("it'S")
    words = s.split(' ')
    result = []
    for word in words:
        if not word:
            result.append("")
            continue
        new_word = word[0].upper() + word[1:].lower()
        result.append(new_word)
    return ' '.join(result)
