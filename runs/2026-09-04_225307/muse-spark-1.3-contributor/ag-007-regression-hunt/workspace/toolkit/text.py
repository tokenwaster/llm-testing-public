def title_case(s: str) -> str:
    res = []
    for i, ch in enumerate(s):
        if ch.isalpha():
            if i == 0:
                res.append(ch.upper())
            else:
                prev = s[i - 1]
                if prev.isalpha():
                    res.append(ch.lower())
                elif prev == "'" and i >= 2 and s[i - 2].isalpha():
                    res.append(ch.lower())
                else:
                    res.append(ch.upper())
        else:
            res.append(ch)
    return "".join(res)


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
