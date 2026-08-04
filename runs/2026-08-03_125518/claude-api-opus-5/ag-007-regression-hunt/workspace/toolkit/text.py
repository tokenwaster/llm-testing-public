import re

_WORD_SPLIT = re.compile(r"(\s+)")


def title_case(s: str) -> str:
    # Unlike str.title(), letters after an apostrophe are not capitalised:
    # "it's a dog's life" -> "It's A Dog's Life".
    parts = _WORD_SPLIT.split(s)
    return "".join(p if p.isspace() else p[:1].upper() + p[1:].lower()
                   for p in parts)


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
