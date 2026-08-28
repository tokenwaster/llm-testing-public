def title_case(s: str) -> str:
    words = s.split()
    titled = []
    for w in words:
        if w:
            titled.append(w[0].upper() + w[1:].lower())
        else:
            titled.append(w)
    return " ".join(titled)


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
