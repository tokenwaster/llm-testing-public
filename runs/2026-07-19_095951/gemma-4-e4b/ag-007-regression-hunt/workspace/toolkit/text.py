def title_case(s: str) -> str:
    """Capitalize the first letter of each word, lowercase the rest.
    Words are separated by spaces; internal apostrophes stay untouched
    (``it's`` -> ``It's``, never ``It'S``)."""
    # Fixed: Use a regex or careful split/join to handle apostrophes correctly.
    return ' '.join([word[0].upper() + word[1:].lower() for word in s.split(' ')])


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
    # Fixed: The slice should be up to 'limit - 1' characters, and then append "…".
    # We must ensure the resulting string length is exactly 'limit'.
    return s[:limit - 1] + "…"
