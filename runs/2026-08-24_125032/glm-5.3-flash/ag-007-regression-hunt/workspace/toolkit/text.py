def title_case(s: str) -> str:
    # Capitalize only at true word starts (after whitespace); unlike
    # str.title(), an apostrophe does not begin a new word.
    out = []
    cap_next = True
    for ch in s:
        if ch.isspace():
            cap_next = True
            out.append(ch)
        elif cap_next:
            out.append(ch.upper())
            cap_next = False
        else:
            out.append(ch.lower())
    return "".join(out)


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
