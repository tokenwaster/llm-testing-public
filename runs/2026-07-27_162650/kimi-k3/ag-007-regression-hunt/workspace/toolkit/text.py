def title_case(s: str) -> str:
    # Capitalize the first character of each whitespace-separated word and
    # lowercase the rest. Unlike str.title(), apostrophes do not start a
    # new word ("it's" -> "It's", not "It'S").
    return " ".join(w.capitalize() for w in s.split(" "))


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
    if len(s) <= limit:
        return s
    return s[: max(limit - 1, 0)] + "…"
