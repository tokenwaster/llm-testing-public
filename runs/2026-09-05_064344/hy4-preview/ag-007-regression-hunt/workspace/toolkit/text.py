import re

_WORD = re.compile(r"[A-Za-z][A-Za-z']*")


def title_case(s: str) -> str:
    # Capitalize the first letter of each word and lowercase the rest, so
    # letters after an apostrophe stay lowercase ("it's" -> "It's").
    return _WORD.sub(lambda m: m.group(0)[0].upper() + m.group(0)[1:].lower(), s)


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
