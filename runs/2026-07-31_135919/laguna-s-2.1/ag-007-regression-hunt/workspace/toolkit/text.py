def title_case(s: str) -> str:
    result = []
    prev = " "
    for ch in s:
        if ch.isalpha():
            if prev == " ":
                result.append(ch.upper())
            else:
                result.append(ch.lower())
        else:
            result.append(ch)
        prev = ch
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
