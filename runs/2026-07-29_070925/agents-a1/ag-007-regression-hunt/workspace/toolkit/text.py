def title_case(s: str) -> str:
    # Custom title case that respects apostrophes within words.
    result = []
    in_word = False
    first_alpha_seen = False
    for ch in s:
        if ch.isspace():
            in_word = False
            first_alpha_seen = False
            result.append(ch)
        else:
            if not in_word:
                in_word = True
                first_alpha_seen = False
            if ch.isalpha():
                if not first_alpha_seen:
                    result.append(ch.upper())
                    first_alpha_seen = True
                else:
                    result.append(ch.lower())
            else:
                # Preserve non-alpha characters (e.g., apostrophes) unchanged.
                result.append(ch)
    return ''.join(result)


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
