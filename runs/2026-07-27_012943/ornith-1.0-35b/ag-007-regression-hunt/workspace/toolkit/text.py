def title_case(s: str) -> str:
    """Capitalize the first letter of each word, lowercase the rest.
    Words are separated by spaces; internal apostrophes stay untouched
    (``it's`` -> ``It's``, never ``It'S``)."""
    result = []
    for word in s.split(" "):
        if "'" in word:
            # capitalize only the very first letter of the word;
            # everything after an apostrophe is left as-is.
            idx = word.index("'")
            prefix = word[:idx]
            suffix = word[idx + 1:]
            result.append(prefix.capitalize() + "'" + suffix)
        else:
            result.append(word.capitalize())
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
