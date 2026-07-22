def title_case(s: str) -> str:
    """Capitalize the first letter of each word, lowercase the rest.
    Words are separated by spaces; internal apostrophes stay untouched
    (``it's`` -> ``It's``, never ``It'S``)."""
    # Implement manually to avoid str.title() behavior with apostrophes.
    # Split on spaces, capitalize first character of each word, lower the rest.
    # Preserve internal apostrophes and other characters as is, only adjust case.
    words = s.split(' ')
    titled_words = []
    for word in words:
        if not word:
            # Preserve empty strings (multiple spaces) as is
            titled_words.append(word)
            continue
        # First character uppercase, rest lowercase
        first = word[0].upper()
        rest = word[1:].lower()
        titled_words.append(first + rest)
    return ' '.join(titled_words)


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
