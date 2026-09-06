def title_case(s: str) -> str:
    out = []
    prev_space = True
    for ch in s:
        if prev_space and ch.isalpha():
            out.append(ch.upper())
        else:
            out.append(ch.lower())
        prev_space = ch.isspace()
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
