def title_case(s: str) -> str:
    """Capitalize the first letter of each word, lowercase the rest.
    Words are separated by spaces; internal apostrophes stay untouched
    (``it's`` -> ``It's``, never ``It'S``)."""
    words = s.split(" ")
    result = []
    for w in words:
        if "'" in w:
            # Split on apostrophe, capitalize first letter of each part
            parts = w.split("'")
            capitalized = "'".join(p.capitalize() for p in parts)
            result.append(capitalized)
        else:
            result.append(w.capitalize())
    return " ".join(result)


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
