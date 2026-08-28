def title_case(s: str) -> str:
    result = []
    capitalize_next = True
    for ch in s:
        if ch.isalpha():
            if capitalize_next:
                result.append(ch.upper())
            else:
                result.append(ch.lower())
            capitalize_next = False
        else:
            result.append(ch)
            # Only set capitalize_next=True if this is not an apostrophe
            if ch != "'":
                capitalize_next = True
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
