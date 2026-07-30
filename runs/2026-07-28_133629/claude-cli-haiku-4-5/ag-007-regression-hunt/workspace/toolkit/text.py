def title_case(s: str) -> str:
    words = s.split(' ')
    result = []
    for word in words:
        parts = word.split("'")
        titled_parts = []
        for i, part in enumerate(parts):
            if i == 0 and part:
                titled_parts.append(part[0].upper() + part[1:].lower())
            else:
                titled_parts.append(part.lower())
        result.append("'".join(titled_parts))
    return ' '.join(result)


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
