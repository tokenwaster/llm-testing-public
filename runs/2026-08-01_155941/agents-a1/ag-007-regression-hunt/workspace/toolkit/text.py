def title_case(s: str) -> str:
    # Capitalize the first letter of each word, keep remaining letters as-is but lowercase after first character.
    words = s.split()
    result = []
    for word in words:
        if word:
            # Uppercase first char, lower rest (preserving apostrophe position)
            cap_first = word[0].upper()
            rest_lower = word[1:].lower()
            result.append(cap_first + rest_lower)
        else:
            result.append('')
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
