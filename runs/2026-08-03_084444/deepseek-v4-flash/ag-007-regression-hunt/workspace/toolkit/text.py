def title_case(s: str) -> str:
    result = []
    next_upper = True
    for ch in s:
        if ch.isalpha():
            if next_upper:
                result.append(ch.upper())
                next_upper = False
            else:
                result.append(ch.lower())
        else:
            result.append(ch)
            if ch == "'":
                # Apostrophes don't start new words
                continue
            next_upper = True
    return "".join(result)


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